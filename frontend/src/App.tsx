import { useState } from "react";
import "./App.css";

type Listing = {
  id: string;
  source: string;
  address: string;
  city: string;
  state: string;
  zip: string;
  price: number;
  bedrooms: number;
  bathrooms: number;
  sqft: number;
  listedDate: string;
  status: string;
  description: string;
  relevanceScore: number;
};

type ApiResponse = {
  results: Listing[];
  pagination: {
    page: number;
    pageSize: number;
    totalResults: number;
    totalPages: number;
  };
};

function App() {
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [minBedrooms, setMinBedrooms] = useState("");
  const [city, setCity] = useState("");
  const [keyword, setKeyword] = useState("");
  const [targetBudget, setTargetBudget] = useState("");
  const [pageSize, setPageSize] = useState("5");

  const [data, setData] = useState<ApiResponse | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const searchListings = async (page = 1) => {
    setLoading(true);
    setError("");

    const params = new URLSearchParams();

    if (minPrice) params.append("minPrice", minPrice);
    if (maxPrice) params.append("maxPrice", maxPrice);
    if (minBedrooms) params.append("minBedrooms", minBedrooms);
    if (city) params.append("city", city);
    if (keyword) params.append("keyword", keyword);
    if (targetBudget) params.append("targetBudget", targetBudget);

    params.append("page", String(page));
    params.append("pageSize", pageSize);

    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/listings/?${params.toString()}`
      );

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.error || "Something went wrong.");
      }

      setData(result);
      setCurrentPage(page);
    } catch (err) {
      setData(null);

      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Unable to load listings.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    searchListings(1);
  };

  const handlePrevious = () => {
    if (currentPage > 1) {
      searchListings(currentPage - 1);
    }
  };

  const handleNext = () => {
    if (
      data &&
      currentPage < data.pagination.totalPages
    ) {
      searchListings(currentPage + 1);
    }
  };

  return (
    <div className="container">
      <h1>Listing Search Service</h1>

      <div className="search-panel">
        <input
          type="number"
          placeholder="Min Price"
          value={minPrice}
          onChange={(e) => setMinPrice(e.target.value)}
        />

        <input
          type="number"
          placeholder="Max Price"
          value={maxPrice}
          onChange={(e) => setMaxPrice(e.target.value)}
        />

        <input
          type="number"
          placeholder="Min Bedrooms"
          value={minBedrooms}
          onChange={(e) => setMinBedrooms(e.target.value)}
        />

        <input
          type="text"
          placeholder="City"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          list="city-options"
        />

        <datalist id="city-options">
          <option value="Springfield" />
          <option value="Fairfax" />
          <option value="Reston" />
          <option value="Vienna" />
          <option value="Manassas" />
          <option value="Chantilly" />
        </datalist>

        <input
          type="text"
          placeholder="Description Keyword"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
        />

        <input
          type="number"
          placeholder="Target Budget"
          value={targetBudget}
          onChange={(e) => setTargetBudget(e.target.value)}
        />

        <select
          value={pageSize}
          onChange={(e) => setPageSize(e.target.value)}
        >
          <option value="3">3 per page</option>
          <option value="5">5 per page</option>
          <option value="10">10 per page</option>
        </select>

        <button onClick={handleSearch}>
          Search
        </button>
      </div>

      {loading && (
        <p className="message">Loading listings...</p>
      )}

      {error && (
        <p className="error">{error}</p>
      )}

      {!loading &&
        !error &&
        data &&
        data.results.length === 0 && (
          <p className="message">
            No listings found.
          </p>
        )}

      {!loading &&
        !error &&
        data &&
        data.results.length > 0 && (
          <>
            <p>
              Found {data.pagination.totalResults} listing(s)
            </p>

            <div className="table-wrapper">
              <table className="listing-table">
                <thead>
                  <tr>
                    <th>Address</th>
                    <th>City</th>
                    <th>Price</th>
                    <th>Beds</th>
                    <th>Baths</th>
                    <th>Sq Ft</th>
                    <th>Listed</th>
                    <th>Status</th>
                    <th>Relevance</th>
                    <th>Description</th>
                  </tr>
                </thead>

                <tbody>
                  {data.results.map((listing) => (
                    <tr key={`${listing.source}-${listing.id}`}>
                      <td>{listing.address}</td>
                      <td>
                        {listing.city}, {listing.state} {listing.zip}
                      </td>
                      <td>${listing.price.toLocaleString()}</td>
                      <td>{listing.bedrooms}</td>
                      <td>{listing.bathrooms}</td>
                      <td>{listing.sqft.toLocaleString()}</td>
                      <td>{listing.listedDate}</td>
                      <td>{listing.status}</td>
                      <td>{listing.relevanceScore.toFixed(4)}</td>
                      <td>{listing.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              </div>

            <div className="pagination">
              <button
                onClick={handlePrevious}
                disabled={currentPage === 1}
              >
                Previous
              </button>

              <span>
                Page {currentPage} of{" "}
                {data.pagination.totalPages}
              </span>

              <button
                onClick={handleNext}
                disabled={
                  currentPage >=
                  data.pagination.totalPages
                }
              >
                Next
              </button>
            </div>
          </>
        )}
    </div>
  );
}

export default App;