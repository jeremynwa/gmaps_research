"""Analysis prompts for different use cases."""

RESTAURANT_ANALYSIS_PROMPT = """Analyste restauration expert. Analyse cet avis : attribue scores 1-100 + keyword produit mentionné pour chaque critère. Si non mentionné : "N/A".

📊 CRITÈRES À ÉVALUER UNIQUEMENT SI MENTIONés (1-100 ou "N/A" si non mentionné):

Pour CHAQUE critère mentionné, fournis:
1. Un score de 1-100 basé sur les questions posées, avec 100 = une très bonne expérience/note client pour ce critère, 50 = une expérience client acceptable/satisfaisante pour ce critère, 10 = une très mauvaise expérience client pour ce critère.
2. Mot-clé(s) (1-3 mots max) indiquant le produit/élément spécifique si mentionné (ou "N/A" si non mentionné)

Critères :
1. offre_profondeur : Y a-t-il assez de choix de produits ? La diversité de l'offre est-elle satisfaisante ?
2. offre_renouvellement : Y a-t-il des produits originaux ? Faudrait-il renouveler l'offre ?
3. offre_clarté : Les menus sont-ils facilement compréhensibles ? Y a-t-il des irritants concernant les suppléments ?
4. offre_fraîcheur : Les produits sont-ils frais ? Par exemple, n'y a-t-il pas de croissant ou pain de la veille ?
5. nourriture_qualité : Les produits sont-ils de bonne qualité, notamment en termes de fraîcheur, de goût et de niveaux de sucre et de sel ?
6. nourriture_santé : Les produits paraissent-ils sains, notamment pas trop gras ou trop sucrés/salés ?
7. nourriture_quantité : La quantité de nourriture est-elle suffisante, notamment en ce qui concerne la taille des portions et des boissons ?
8. nourriture_présentation : La présentation des produits et l'emballage sont-ils appropriés ?
9. prix_niveau_global : Quel est le niveau de prix global perçu, sans tenir compte de la qualité ?
10. prix_niveau_menus : Quel est le niveau de prix des formules (ex. : petit-déjeuner, déjeuner, combo), sans tenir compte de la qualité ?
11. prix_rapport_qualité : Quel est le niveau de rapport qualité-prix perçu ?
12. prix_promotions : Il y a-t-il suffisemment de bonnes affaires ou promotions ?
13. rapidité_service : Quelle est la rapidité du service client ? Y a-t-il eu des abandons dus à la lenteur ?
14. atmosphère_entretien : Le restaurant est-il bien entretenu ? Le restaurant paraît-il vieillissant ?
15. atmosphère_confort : Les places assises sont-elles confortables ? L'espace dans le restaurant est-il suffisant ?
16. atmosphère_parcours : Le parcours du client sur le site est-il fluide ? Était-il facile de trouver les offres et les prix ?
17. force_vente : Le personnel est-il sympathique et efficace ? Donne-t-il de bons conseils ? Essaie-t-il de forcer la vente de produits ?
18. hygiène : Le niveau d'hygiène et de propreté est-il adéquat ?
19. propreté_vitrine : Est-ce que la vitrine est mise en avant ?  Produits bien rangées, vitrine pas embuée et les produits sont bien visibles ?
20. nps : Ce client recommanderait-il ce site ou reviendrait-il dans le futur ?
21. produit_cher : Y a-t-il un ou plusieurs produits décrits comme étant chers ?

RÈGLES:
- Évalue selon avis uniquement, PAS la note
- Scores multiples de 10 uniquement
- Score SI clairement mentionné, sinon "N/A"
- NE PAS extrapoler ou inventer des scores
- Keywords: produit spécifique ("café", "sandwich") ou "Personnel" si nom de personne, sinon "N/A"

JSON (format strict avec accolades simples):
{
  "offre_profondeur_score": 85, "offre_profondeur_keyword": "sandwiches",
  "offre_renouvellement_score": 70, "offre_renouvellement_keyword": "smoothie",
  "offre_clarte_score": 70, "offre_clarte_keyword": "menu",
  "offre_fraicheur_score": 90, "offre_fraicheur_keyword": "croissants",
  "nourriture_qualite_score": 90, "nourriture_qualite_keyword": "café",
  "nourriture_quantite_score": 80, "nourriture_quantite_keyword": "portions",
  "nourriture_presentation_score": 75, "nourriture_presentation_keyword": "emballage",
  "nourriture_sante_score": 95, "nourriture_sante_keyword": "salades",
  "prix_niveau_global_score": 60, "prix_niveau_global_keyword": "général",
  "prix_niveau_menus_score": 65, "prix_niveau_menus_keyword": "formule",
  "prix_rapport_qualite_score": 70, "prix_rapport_qualite_keyword": "général",
  "prix_promotions_score": 80, "prix_promotions_keyword": "offres",
  "rapidite_service_score": 85, "rapidite_service_keyword": "caisse",
  "atmosphere_entretien_score": 80, "atmosphere_entretien_keyword": "salle",
  "atmosphere_confort_score": 75, "atmosphere_confort_keyword": "places",
  "atmosphere_parcours_score": 90, "atmosphere_parcours_keyword": "comptoir",
  "force_vente_score": 90, "force_vente_keyword": "personnel",
  "hygiene_score": 95, "hygiene_keyword": "toilettes",
  "proprete_vitrine_score": 30, "proprete_vitrine_keyword": "vitrine",
  "nps_score": 40, "nps_keyword": "N/A",
  "produit_cher_score": 20, "produit_cher_keyword": "café"
}"""


def get_prompt(prompt_type: str = "restaurant") -> str:
    """Get prompt by type."""
    prompts = {
        "restaurant": RESTAURANT_ANALYSIS_PROMPT,
        # Add more prompt types here
    }
    return prompts.get(prompt_type, RESTAURANT_ANALYSIS_PROMPT)