function Results({ valuationData }) {
  return (
    <div>
      <h2>📊 Results</h2>
      {Object.entries(valuationData).map(([file, data]) => (
        <pre key={file}>
          {JSON.stringify(data, null, 2)}
        </pre>
      ))}
    </div>
  );
}

export default Results;
