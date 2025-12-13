import React, { useState } from "react";
import { uploadFile, getContract } from "./api";

export default function App(){
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [contractId, setContractId] = useState("");

  const onUpload = async () => {
    if (!file) return alert("pick file");
    const res = await uploadFile(file);
    setResult(res);
  };

  const fetchById = async () => {
    if (!contractId) return;
    const r = await getContract(contractId);
    setResult(r);
  };

  return (
    <div style={{padding:20, fontFamily:"Arial"}}>
      <h2>Car Lease Contract Review — Demo</h2>
      <div>
        <input type="file" onChange={(e)=>setFile(e.target.files[0])} />
        <button onClick={onUpload}>Upload & Analyze</button>
      </div>
      <div style={{marginTop:20}}>
        <input placeholder="Contract ID" value={contractId} onChange={e=>setContractId(e.target.value)} />
        <button onClick={fetchById}>Fetch Contract</button>
      </div>
      <pre style={{whiteSpace:"pre-wrap", background:"#fafafa", padding:10, marginTop:20}}>
        { result ? JSON.stringify(result, null, 2) : "No results yet" }
      </pre>
    </div>
  );
}
