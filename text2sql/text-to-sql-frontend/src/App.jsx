import React, { useState } from "react";

export default function App() {
  const [question, setQuestion] = useState("");
  const [sql, setSQL] = useState("");
  const [results, setResults] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [feedback, setFeedback] = useState("");
  const [file, setFile] = useState(null);

  const handleUploadSchema = async () => {
    setError("");
    if (!file) {
      setError("Please select a JSON schema file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch("/upload-schema", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (data.message) alert(data.message);
      else setError(data.error || "Upload failed");
    } catch (err) {
      setError("Schema upload failed.");
    }
  };

  const handleAsk = async () => {
    setLoading(true);
    setError("");
    setSQL("");
    setResults([]);

    try {
      const response = await fetch("/generate-sql", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await response.json();

      if (data.error) {
        setError(data.error);
      } else {
        setSQL(data.sql);
        setResults(data.results || []);
      }
    } catch (err) {
      setError("Request failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleFeedback = async () => {
    try {
      const response = await fetch("/submit-feedback", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          generated_sql: sql,
          feedback,
        }),
      });

      const data = await response.json();
      alert(data.message || "Feedback submitted");
    } catch (err) {
      console.error("Failed to submit feedback:", err);
      alert("Failed to submit feedback");
    }
  };

  const handleReset = () => {
    setQuestion("");
    setSQL("");
    setResults([]);
    setError("");
    setFeedback("");
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Text-to-SQL Assistant</h1>

      <h2 className="text-lg font-semibold mb-1">Upload Schema</h2>
      <input
        type="file"
        accept=".json"
        className="mb-2"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button
        className="bg-green-600 text-white px-4 py-2 rounded mb-6 hover:bg-green-700"
        onClick={handleUploadSchema}
      >
        Upload Schema
      </button>

      <h2 className="text-lg font-semibold mb-1">Ask a Question</h2>
      <textarea
        className="w-full border p-3 rounded mb-4"
        rows="3"
        placeholder="Ask something about your database..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />

      <div className="mb-4">
        <button
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 mr-2"
          onClick={handleAsk}
          disabled={loading}
        >
          {loading ? "Generating..." : "Ask"}
        </button>

        <button
          className="bg-gray-600 text-white px-4 py-2 rounded hover:bg-gray-700"
          onClick={handleReset}
        >
          Reset
        </button>
      </div>

      {error && <p className="text-red-600 mt-4">{error}</p>}

      {sql && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-2">Generated SQL</h2>
          <pre className="bg-gray-100 p-3 rounded text-sm overflow-auto">{sql}</pre>
        </div>
      )}

      {results.length > 0 && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-2">Results</h2>
          <div className="overflow-auto">
            <table className="w-full border-collapse border">
              <thead>
                <tr>
                  {Object.keys(results[0]).map((key) => (
                    <th
                      key={key}
                      className="border px-3 py-2 bg-gray-200 text-left"
                    >
                      {key}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {results.map((row, idx) => (
                  <tr key={idx}>
                    {Object.values(row).map((value, i) => (
                      <td key={i} className="border px-3 py-2">
                        {value}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {sql && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold mb-2">Submit Feedback</h2>
          <textarea
            className="w-full border p-3 rounded mb-2"
            rows="3"
            placeholder="Tell us if the result was wrong or unexpected..."
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          />
          <button
            className="bg-yellow-600 text-white px-4 py-2 rounded hover:bg-yellow-700"
            onClick={handleFeedback}
          >
            Submit Feedback
          </button>
        </div>
      )}
    </div>
  );
}
