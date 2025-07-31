import React from 'react';
import '../styles/App.css';


function Comparator({ cards }) {
  return (
    <div className="comparator">
      {cards.map((card, index) => (
        <div key={index} className="comparator-card">
          <img src={card.image} alt={card.name} />
          <h2>{card.name}</h2>
          <p>{card.description}</p>
          <ul>
            {card.attributes.map((attr, idx) => (
              <li key={idx}>{attr}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default Comparator;