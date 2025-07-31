import React, { useState } from 'react';
import '../styles/App.css';


function SearchBar({ onSearch }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(url);
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Entrez un lien Fandom..."
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <button type="submit">Scraper</button>
    </form>
  );
}

export default SearchBar;