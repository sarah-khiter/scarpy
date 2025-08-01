import React, { useState, useEffect } from 'react';
import './App.css';

function SearchBar({ onSearch, isLoading }) {
  const [url, setUrl] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch(url);
  };

  return (
    <form onSubmit={handleSubmit} className="search-bar">
      <input
        type="url"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        placeholder="Entrez l'URL du wiki Fandom (ex: https://leagueoflegends.fandom.com/)"
        required
        className="search-input"
      />
      <button type="submit" disabled={isLoading} className="search-button">
        {isLoading ? 'Scraping en cours...' : 'Scraper'}
      </button>
    </form>
  );
}

function CharacterCard({ character, onSelect, isSelected, isCompareMode }) {
  // Fonction helper pour afficher les détails s'ils existent
  const renderDetails = () => {
    if (!character) return null;

    const details = [
      { label: 'Type', value: character.type },
      { label: 'Rôle', value: character.role },
      { label: 'Classe', value: character.class_name },
      { label: 'Origine', value: character.origin },
      { label: 'Affiliation', value: character.affiliation },
      { label: 'Occupation', value: character.occupation }
    ].filter(detail => detail.value && detail.value !== "null" && detail.value !== "undefined");

    if (details.length === 0) return null;

    return (
      <div className="character-details">
        {details.map((detail, index) => (
          <div key={index} className="detail-item">
            <span className="detail-label">{detail.label}:</span>
            <span className="detail-value">{detail.value}</span>
          </div>
        ))}
      </div>
    );
  };

  if (!character || !character.name) {
    return null;
  }

  return (
    <div className={`character-card ${isSelected ? 'selected' : ''}`}>
      <div className="character-image">
        <img 
          src={character.image_url || '/placeholder.png'} 
          alt={character.name} 
          onError={(e) => {
            e.target.onerror = null;
            e.target.src = '/placeholder.png';
          }} 
        />
      </div>
      <div className="character-info">
        <h3>{character.name}</h3>
        
        {renderDetails()}

        <div className="character-actions">
          {character.url && (
            <a 
              href={character.url} 
              target="_blank" 
              rel="noopener noreferrer"
              className="character-link"
            >
              Voir la page
            </a>
          )}
          {isCompareMode && (
            <button 
              onClick={() => onSelect(character)}
              className={`compare-select-button ${isSelected ? 'selected' : ''}`}
            >
              {isSelected ? 'Sélectionné' : 'Sélectionner'}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

function ComparisonView({ characters, onClose }) {
  if (!characters || characters.length !== 2) return null;

  return (
    <div className="comparison-overlay">
      <div className="comparison-container">
        <button className="close-comparison" onClick={onClose}>×</button>
        <h2>Comparaison des personnages</h2>
        <div className="comparison-grid">
          {characters.map((character, index) => (
            <div key={index} className="comparison-character">
              <div className="comparison-image">
                <img 
                  src={character.image_url} 
                  alt={character.name}
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = '/placeholder.png';
                  }}
                />
              </div>
              <h3>{character.name}</h3>
              <a 
                href={character.url}
                target="_blank"
                rel="noopener noreferrer"
                className="character-link"
              >
                Voir la page
              </a>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function WikiList({ wikis, onWikiSelect, selectedWiki }) {
  if (!wikis.length) return null;

  return (
    <div className="wiki-list">
      <h2>Wikis scrapés</h2>
      <div className="wiki-buttons">
        {wikis.map(wiki => (
          <button
            key={wiki.name}
            onClick={() => onWikiSelect(wiki.name)}
            className={`wiki-button ${selectedWiki === wiki.name ? 'selected' : ''}`}
          >
            {wiki.name}
            <span className="character-count">({wiki.character_count} personnages)</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function App() {
  const [characters, setCharacters] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [wikis, setWikis] = useState([]);
  const [selectedWiki, setSelectedWiki] = useState(null);
  const [isCompareMode, setIsCompareMode] = useState(false);
  const [selectedCharacters, setSelectedCharacters] = useState([]);
  const [showComparison, setShowComparison] = useState(false);

  // Charger la liste des wikis au démarrage
  useEffect(() => {
    fetchWikis();
  }, []);

  const handleWikiSelect = async (wikiName) => {
    setSelectedWiki(wikiName);
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`http://localhost:5000/wiki/${wikiName}`);
      const data = await response.json();
      console.log('Données reçues du wiki:', data); // Debug

      if (response.ok && data.success) {
        if (Array.isArray(data.data)) {
          setCharacters(data.data);
          console.log('Personnages chargés:', data.data.length);
        } else {
          console.error('Les données ne sont pas un tableau:', data.data);
          setError('Format de données incorrect');
        }
      } else {
        setError(data.error || 'Erreur lors de la récupération des données');
      }
    } catch (err) {
      console.error('Erreur complète:', err);
      setError('Erreur de connexion au serveur');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCharacterSelect = (character) => {
    setSelectedCharacters(prev => {
      if (prev.find(c => c.name === character.name)) {
        return prev.filter(c => c.name !== character.name);
      }
      if (prev.length < 2) {
        return [...prev, character];
      }
      return prev;
    });
  };

  const handleCompare = () => {
    if (selectedCharacters.length === 2) {
      setShowComparison(true);
    }
  };

  const closeComparison = () => {
    setShowComparison(false);
    setSelectedCharacters([]);
    setIsCompareMode(false);
  };

  const handleSearch = async (url) => {
    setIsLoading(true);
    setError(null);
    setCharacters([]);
    
    try {
      const response = await fetch('http://localhost:5000/scrape', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();
      console.log('Données reçues du scraping:', data); // Debug

      if (!response.ok) {
        throw new Error(data.error || 'Erreur lors du scraping');
      }

      if (data.success) {
        if (Array.isArray(data.data)) {
          setCharacters(data.data);
          console.log('Personnages chargés:', data.data.length);
        } else {
          console.error('Les données ne sont pas un tableau:', data.data);
          setError('Format de données incorrect');
        }
        // Rafraîchir la liste des wikis après un nouveau scraping
        fetchWikis();
      } else {
        setError(data.error || 'Erreur: données non valides');
      }
    } catch (err) {
      console.error('Erreur complète:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchWikis = async () => {
    try {
      const response = await fetch('http://localhost:5000/wikis');
      const data = await response.json();
      console.log('Liste des wikis reçue:', data); // Debug

      if (response.ok && data.success) {
        if (Array.isArray(data.wikis)) {
          setWikis(data.wikis);
          console.log('Wikis chargés:', data.wikis.length);
        } else {
          console.error('La liste des wikis n\'est pas un tableau:', data.wikis);
        }
      } else {
        console.error('Erreur lors de la récupération des wikis:', data.error);
      }
    } catch (err) {
      console.error('Erreur lors de la récupération des wikis:', err);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Fandom Wiki Scraper</h1>
        <p className="subtitle">Explorez et extrayez des informations de n'importe quel wiki Fandom</p>
        <SearchBar onSearch={handleSearch} isLoading={isLoading} />
      </header>

      <WikiList 
        wikis={wikis} 
        onWikiSelect={handleWikiSelect}
        selectedWiki={selectedWiki}
      />

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {isLoading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Chargement en cours...</p>
        </div>
      )}

      {characters.length > 0 && (
        <>
          <div className="results-info">
            <h2>{characters.length} personnages trouvés</h2>
            <div className="compare-controls">
              <button 
                className={`compare-button ${isCompareMode ? 'active' : ''}`}
                onClick={() => {
                  setIsCompareMode(!isCompareMode);
                  if (!isCompareMode) {
                    setSelectedCharacters([]);
                  }
                }}
              >
                {isCompareMode ? 'Annuler la comparaison' : 'Comparer des personnages'}
              </button>
              {isCompareMode && (
                <button 
                  className="compare-action-button"
                  disabled={selectedCharacters.length !== 2}
                  onClick={handleCompare}
                >
                  Comparer ({selectedCharacters.length}/2)
                </button>
              )}
            </div>
          </div>

          <div className="characters-grid">
            {characters.map((character, index) => (
              <CharacterCard 
                key={`${character.name}-${index}`} 
                character={character}
                isCompareMode={isCompareMode}
                isSelected={selectedCharacters.some(c => c.name === character.name)}
                onSelect={handleCharacterSelect}
              />
            ))}
          </div>
        </>
      )}

      {showComparison && (
        <ComparisonView 
          characters={selectedCharacters}
          onClose={closeComparison}
        />
      )}
    </div>
  );
}

export default App;
