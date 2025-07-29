"use client";

import { useState, useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { Loader2, UploadCloud } from "lucide-react";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<any>(null);
  const [jobDesc, setJobDesc] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setFile(acceptedFiles[0]);
    setResult(null);
    setError("");
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': [],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': []
    }
  });

  const handleSubmit = async () => {
    if (!file || !jobDesc) {
      setError("❗ Please provide both a resume and a job description.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_description", jobDesc);

    setLoading(true);
    setResult(null);
    setError("");

    try {
      const res = await fetch("http://localhost:8000/analyze", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Analysis failed");

      const data = await res.json();
      setResult({
        skills: [],
        education: [],
        experience: [],
        ...data,
      });
    } catch (err) {
      console.error(err);
      setError("❌ Upload or analysis error.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-6">
      <h1 className="text-4xl font-bold text-center">🧠 AI Resume Analyzer</h1>

      <textarea
        rows={5}
        placeholder="Paste job description here..."
        className="w-full p-3 border rounded-md border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-400"
        value={jobDesc}
        onChange={(e) => setJobDesc(e.target.value)}
        disabled={loading}
      />

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition ${
          isDragActive ? "border-blue-500" : "border-gray-400"
        } ${loading ? "opacity-50" : ""}`}
      >
        <input {...getInputProps()} disabled={loading} />
        <div className="flex flex-col items-center space-y-2">
          <UploadCloud className="w-8 h-8 text-gray-600" />
          <p className="text-lg font-medium">
            {file ? file.name : "Drag & drop or click to upload your resume"}
          </p>
          <p className="text-sm text-gray-500">Supported: .pdf, .docx</p>
        </div>
      </div>

      <button
        onClick={handleSubmit}
        disabled={loading || !file}
        className="bg-blue-600 text-white font-semibold px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin" /> Analyzing...
          </span>
        ) : (
          "Submit"
        )}
      </button>

      {error && <div className="text-red-600 text-center text-sm">{error}</div>}

      {result && (
        <div className="bg-white rounded-lg shadow-md p-6 space-y-4">
          <h2 className="text-xl font-bold text-blue-700">Summary</h2>
          <p className="text-gray-800">{result.summary}</p>

          <div>
            <h3 className="font-semibold text-green-700">Top Skills</h3>
            {Array.isArray(result.skills) && result.skills.length > 0 ? (
              <ul className="list-disc list-inside text-sm">
                {result.skills.map((skill: string, idx: number) => (
                  <li key={idx}>{skill}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No skills detected.</p>
            )}
          </div>

          <div>
            <h3 className="font-semibold text-blue-700">Education</h3>
            {Array.isArray(result.education) && result.education.length > 0 ? (
              <ul className="list-disc list-inside text-sm">
                {result.education.map((edu: string, idx: number) => (
                  <li key={idx}>{edu}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No education found.</p>
            )}
          </div>

          <div>
            <h3 className="font-semibold text-indigo-700">Experience</h3>
            {Array.isArray(result.experience) && result.experience.length > 0 ? (
              <ul className="list-disc list-inside text-sm">
                {result.experience.map((exp: string, idx: number) => (
                  <li key={idx}>{exp}</li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-gray-500">No experience found.</p>
            )}
          </div>

          <div>
            <h3 className="font-semibold text-purple-700 mb-1">Full Resume Text</h3>
            <pre className="bg-gray-100 border p-3 rounded max-h-64 overflow-y-auto text-sm whitespace-pre-wrap">
              {result.text}
            </pre>
          </div>

          <div className="space-y-1">
            <h3 className="text-lg font-bold text-green-600">
              ATS Match Score: {result.ats_score ?? result.score ?? 0}%
            </h3>
            <p className="text-sm">
              📊 <strong>TF-IDF Score:</strong> {result.score ?? 0}%
            </p>
            <p className="text-sm">
              🔍 <strong>Keyword Match:</strong> {result.keyword_match_score ?? 0}%
            </p>
            <p className="text-sm">
              🧩 <strong>Section Bonus:</strong> {result.section_bonus ?? 0} pts
            </p>
            {result.suggestion && (
              <p className="text-yellow-700 font-semibold">{result.suggestion}</p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
