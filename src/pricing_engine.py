"""
Moteur de pricing dynamique pour l'hôtellerie
Auteur: David Michel-Larrieux
"""

import pandas as pd
import numpy as np
from scipy.optimize import minimize_scalar
import warnings
warnings.filterwarnings('ignore')

class PricingEngine:
    """
    Moteur de pricing dynamique basé sur la demande prédite
    
    Utilise des algorithmes d'optimisation pour calculer le prix optimal
    qui maximise le RevPAR tout en respectant les contraintes métier.
    """
    
    def __init__(self):
        self.pricing_rules = {
            'Standard': {
                'base_price': 100,
                'min_price': 80,
                'max_price': 200,
                'elasticity': -1.2  # Élasticité prix-demande
            },
            'Deluxe': {
                'base_price': 150,
                'min_price': 120,
                'max_price': 300,
                'elasticity': -1.5
            },
            'Suite': {
                'base_price': 250,
                'min_price': 200,
                'max_price': 500,
                'elasticity': -1.8
            }
        }
        
    def demand_function(self, price, base_demand, elasticity, competitor_avg_price):
        """
        Fonction de demande basée sur l'élasticité prix
        
        Args:
            price (float): Prix proposé
            base_demand (float): Demande de base (sans effet prix)
            elasticity (float): Élasticité prix-demande
            competitor_avg_price (float): Prix moyen concurrence
            
        Returns:
            float: Demande ajustée selon le prix
        """
        # Effet du prix relatif à la concurrence
        price_ratio = price / competitor_avg_price
        
        # Fonction de demande avec élasticité
        demand_adjustment = (price_ratio ** elasticity)
        adjusted_demand = base_demand * demand_adjustment
        
        return np.clip(adjusted_demand, 0.05, 0.98)
    
    def revenue_function(self, price, base_demand, elasticity, competitor_avg_price):
        """
        Calcule le revenu (RevPAR) pour un prix donné
        
        Returns:
            float: RevPAR = Price × Occupancy Rate
        """
        demand = self.demand_function(price, base_demand, elasticity, competitor_avg_price)
        return price * demand
    
    def calculate_optimal_price(self, 
                              predicted_demand, 
                              room_type='Standard',
                              competitor_prices=None,
                              min_price=None,
                              max_price=None,
                              optimization_target='revpar'):
        """
        Calcule le prix optimal pour maximiser le RevPAR
        
        Args:
            predicted_demand (float): Taux d'occupation prédit (0-1)
            room_type (str): Type de chambre
            competitor_prices (list): Prix de la concurrence
            min_price (float): Prix minimum (optionnel)
            max_price (float): Prix maximum (optionnel)
            optimization_target (str): 'revpar' ou 'occupancy'
            
        Returns:
            dict: Prix optimal et métriques associées
        """
        # Récupération des règles de pricing
        rules = self.pricing_rules.get(room_type, self.pricing_rules['Standard'])
        
        # Prix de contrainte
        min_p = min_price or rules['min_price']
        max_p = max_price or rules['max_price']
        
        # Prix moyen concurrence
        if competitor_prices:
            competitor_avg = np.mean(competitor_prices)
        else:
            competitor_avg = rules['base_price']
        
        # Fonction objective à maximiser
        def objective(price):
            if optimization_target == 'revpar':
                return -self.revenue_function(price, predicted_demand, 
                                            rules['elasticity'], competitor_avg)
            else:  # occupancy
                return -self.demand_function(price, predicted_demand,
                                           rules['elasticity'], competitor_avg)
        
        # Optimisation
        result = minimize_scalar(objective, bounds=(min_p, max_p), method='bounded')
        optimal_price = result.x
        
        # Calcul des métriques finales
        final_demand = self.demand_function(optimal_price, predicted_demand,
                                          rules['elasticity'], competitor_avg)
        final_revpar = optimal_price * final_demand
        
        # Recommandations business
        recommendations = self._generate_recommendations(
            optimal_price, final_demand, competitor_prices, rules
        )
        
        return {
            'optimal_price': round(optimal_price, 2),
            'predicted_occupancy': round(final_demand, 3),
            'predicted_revpar': round(final_revpar, 2),
            'base_demand': predicted_demand,
            'competitor_avg_price': competitor_avg,
            'price_vs_competition': round((optimal_price / competitor_avg - 1) * 100, 1),
            'recommendations': recommendations
        }
    
    def _generate_recommendations(self, price, demand, competitor_prices, rules):
        """Génère des recommandations business"""
        recommendations = []
        
        if competitor_prices:
            comp_avg = np.mean(competitor_prices)
            if price > comp_avg * 1.15:
                recommendations.append("⚠️ Prix significativement au-dessus de la concurrence")
            elif price < comp_avg * 0.85:
                recommendations.append("💡 Opportunité d'augmentation de prix")
        
        if demand > 0.90:
            recommendations.append("🔥 Forte demande - Considérer une hausse de prix")
        elif demand < 0.60:
            recommendations.append("📉 Demande faible - Envisager une promotion")
        
        if price <= rules['min_price'] * 1.05:
            recommendations.append("⛔ Prix proche du minimum - Vérifier la stratégie")
        elif price >= rules['max_price'] * 0.95:
            recommendations.append("💰 Prix premium - S'assurer de la valeur ajoutée")
        
        return recommendations
    
    def scenario_analysis(self, base_demand, room_type='Standard', 
                         competitor_prices=None, price_range=None):
        """
        Analyse de scénarios pour différents niveaux de prix
        
        Returns:
            pd.DataFrame: Analyse complète des scénarios
        """
        rules = self.pricing_rules.get(room_type, self.pricing_rules['Standard'])
        
        if price_range is None:
            price_range = np.arange(rules['min_price'], rules['max_price'], 5)
        
        if competitor_prices:
            competitor_avg = np.mean(competitor_prices)
        else:
            competitor_avg = rules['base_price']
        
        scenarios = []
        for price in price_range:
            demand = self.demand_function(price, base_demand, 
                                        rules['elasticity'], competitor_avg)
            revpar = price * demand
            
            scenarios.append({
                'price': price,
                'occupancy_rate': demand,
                'revpar': revpar,
                'vs_competition': (price / competitor_avg - 1) * 100
            })
        
        return pd.DataFrame(scenarios)
    
    def get_pricing_insights(self, historical_data):
        """
        Analyse des performances historiques de pricing
        
        Args:
            historical_data (pd.DataFrame): Données historiques (price, occupancy, date)
            
        Returns:
            dict: Insights et recommandations
        """
        df = historical_data.copy()
        df['revpar'] = df['price'] * df['occupancy_rate']
        df['date'] = pd.to_datetime(df['date'])
        
        # Métriques globales
        insights = {
            'avg_price': df['price'].mean(),
            'avg_occupancy': df['occupancy_rate'].mean(),
            'avg_revpar': df['revpar'].mean(),
            'price_volatility': df['price'].std() / df['price'].mean(),
            'occupancy_volatility': df['occupancy_rate'].std()
        }
        
        # Analyse par jour de la semaine
        df['day_name'] = df['date'].dt.day_name()
        daily_performance = df.groupby('day_name').agg({
            'price': 'mean',
            'occupancy_rate': 'mean',
            'revpar': 'mean'
        }).round(2)
        
        insights['daily_performance'] = daily_performance
        
        # Corrélation prix-occupation
        correlation = df['price'].corr(df['occupancy_rate'])
        insights['price_occupancy_correlation'] = correlation
        
        # Opportunités d'optimisation
        opportunities = []
        if correlation > -0.3:  # Faible sensibilité au prix
            opportunities.append("💡 Demande peu sensible au prix - Potentiel d'augmentation")
        
        if insights['price_volatility'] > 0.15:
            opportunities.append("📊 Forte volatilité prix - Standardiser la stratégie")
        
        insights['opportunities'] = opportunities
        
        return insights

# Exemple d'utilisation
if __name__ == "__main__":
    # Test du moteur de pricing
    pricer = PricingEngine()
    
    # Scénario 1: Pricing optimal
    result = pricer.calculate_optimal_price(
        predicted_demand=0.75,
        room_type='Deluxe',
        competitor_prices=[140, 160, 155, 170],
        optimization_target='revpar'
    )
    
    print("🎯 Pricing Optimal:")
    print(f"Prix recommandé: {result['optimal_price']}€")
    print(f"Occupation prédite: {result['predicted_occupancy']*100:.1f}%")
    print(f"RevPAR prédit: {result['predicted_revpar']}€")
    print(f"vs Concurrence: {result['price_vs_competition']:+.1f}%")
    print("\n💡 Recommandations:")
    for rec in result['recommendations']:
        print(f"  {rec}")
    
    # Scénario 2: Analyse de sensibilité
    print("\n📊 Analyse de scénarios:")
    scenarios = pricer.scenario_analysis(
        base_demand=0.75,
        room_type='Deluxe',
        competitor_prices=[140, 160, 155, 170]
    )
    
    # Top 5 des meilleurs RevPAR
    top_scenarios = scenarios.nlargest(5, 'revpar')
    print(top_scenarios[['price', 'occupancy_rate', 'revpar']].to_string(index=False))
