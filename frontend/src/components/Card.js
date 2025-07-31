import React from 'react';
import '../styles/App.css';


function Card({ data, onSelect }) {
  return (
    <div className="card" onClick={() => onSelect(data)}>
  <img src={data.image} alt={data.name} />
  <h2>{data.name}</h2>
  <p>{data.description}</p>
  <ul>
    {data.attributes.map((attr, index) => (
      <li key={index}>{attr}</li>
    ))}
  </ul>
</div>

  );
}

export default Card;