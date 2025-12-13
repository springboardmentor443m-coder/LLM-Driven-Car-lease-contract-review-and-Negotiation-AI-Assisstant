const API_BASE = "http://localhost:8000";

export async function uploadFile(file) {
  const fd = new FormData();
  fd.append("file", file);

  const res = await fetch(`${API_BASE}/upload`, {
    method: "POST",
    body: fd,
  });

  return res.json();
}

export async function getContract(id) {
  const res = await fetch(`${API_BASE}/contract/${id}`);
  return res.json();
}
