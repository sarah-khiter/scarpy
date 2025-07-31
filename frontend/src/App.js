import React, { useState } from "react";
import SearchBar from "./components/SearchBar";
import Card from "./components/Card";
import Comparator from "./components/Comparator";
import "./styles/App.css";

function App() {
  const [cards, setCards] = useState([]); // Résultats scrappés
  const [compareList, setCompareList] = useState([]); // Cartes sélectionnées pour comparaison

  const handleSearch = (url) => {
    // Simule des données scrappées
    const fakeData = [
      {
        name: "Personnage 1",
        description: "Description du personnage 1.",
        image: "https://via.placeholder.com/300",
        attributes: ["Force: 80", "Vitesse: 70", "Intelligence: 90"],
      },
      {
        name: "Personnage 2",
        description: "Description du personnage 2.",
        image: "https://via.placeholder.com/300",
        attributes: ["Force: 75", "Vitesse: 85", "Intelligence: 88"],
      },
    ];
    setCards(fakeData);
  };

  const handleSelectCard = (card) => {
    if (compareList.length < 2 && !compareList.includes(card)) {
      setCompareList([...compareList, card]);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="header">
        <h1>Fandom Scraper</h1>
        <p>Recherchez, explorez et comparez facilement vos personnages préférés.</p>
      </header>

      {/* Barre de recherche */}
      <section className="search-section">
        <SearchBar onSearch={handleSearch} />
      </section>

      {/* Liste des cartes */}
      <section className="cards-container">
        {cards.length === 0 ? (
          <p className="empty-message">Aucun résultat pour le moment. Lancez une recherche !</p>
        ) : (
          cards.map((card, index) => (
            <Card key={index} data={card} onSelect={handleSelectCard} />
          ))
        )}
      </section>

      {/* Comparateur */}
      {compareList.length > 0 && (
        <section className="compare-section">
          <h2>Comparaison</h2>
          <Comparator cards={compareList} />
        </section>
      )}
    </div>
  );
}

export default App;
