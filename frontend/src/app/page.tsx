// frontend/app/page.tsx
"use client";

import { useState } from "react";

export default function Home() {
  const [result, setResult] = useState<any>(null);
  const [jobDesc, setJobDesc] = useState("");
  const [loading, setLoading] = useState(false);

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDesc);

    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        console.error("Failed to analyze resume:", res.statusText);
        return;
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error("Upload error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 space-y-4 max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-4">🧠 AI Resume Analyzer</h1>

      <textarea
        rows={6}
        placeholder="Paste Job Description here..."
        className="w-full p-2 border rounded"
        value={jobDesc}
        onChange={(e) => setJobDesc(e.target.value)}
      />

      <label className="block border-2 border-dashed border-gray-400 p-6 rounded-lg text-center cursor-pointer hover:border-blue-500 transition">
        <input
          type="file"
          accept=".pdf,.docx"
          className="hidden"
          onChange={handleFileChange}
        />
        <p>📎 Click or drag your resume file here</p>
        <p className="text-sm text-gray-500">Supported: .pdf, .docx</p>
      </label>

      {loading && (
        <div className="mt-4 text-blue-500 animate-pulse">Analyzing...</div>
      )}

      {result && (
        <div className="mt-6 bg-gray-100 text-black p-4 rounded shadow space-y-4">
          <div>
            <h2 className="text-xl font-bold text-blue-700 mb-2">Summary:</h2>
            <p>{result.summary}</p>
          </div>

          <div>
            <h3 className="font-semibold text-green-700">Top Skills:</h3>
            <ul className="list-disc list-inside">
              {result.skills.map((skill: string, idx: number) => (
                <li key={idx}>{skill}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-purple-700">Full Resume Text:</h3>
            <pre className="bg-white border p-4 rounded max-h-[300px] overflow-y-auto text-sm whitespace-pre-wrap">
              {result.text}
            </pre>
          </div>

          {result.score !== null && (
            <div className="text-green-600 font-bold text-lg">
              Match Score: {result.score}%
            </div>
          )}
        </div>
      )}
    </div>
  );
}
