"use client";

import { ChangeEvent, useState } from "react";

type UploadStatus = "idle" | "processing" | "sucess" | "error";

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [fastMode, setFastMode] = useState<boolean>(false);
  const [status, setStatus] = useState<UploadStatus>("idle");

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  }

  async function handleSubmit(e: React.FormEvent<HTMLElement>) {
    e.preventDefault();
    if (!file) return;

    setStatus("processing");
    const formData = new FormData();
    formData.append("file", file);
    formData.append("code", language);
    formData.append("password", password);
    formData.append("fastmode", fastMode ? "true" : "false");

    console.log(formData);

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const filename = `${language}.properties`;
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);

      setStatus("sucess");
    } catch {
      setStatus("error");
    }
  }

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="file">File:</label>
          <input type="file" id="file" onChange={handleFileChange} />
        </div>

        <div>
          <label htmlFor="language">Language:</label>
          <input
            type="text"
            id="language"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            placeholder="Enter language"
          />
        </div>

        <div>
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Enter password"
          />
        </div>

        <div>
          <label htmlFor="fastMode">
            <input
              type="checkbox"
              id="fastMode"
              checked={fastMode}
              onChange={(e) => setFastMode(e.target.checked)}
            />
            Fast Mode
          </label>
        </div>

        {status === "idle" || status === "sucess" ? (
          <button type="submit">Submit</button>
        ) : status === "processing" ? (
          <div>Processing your upload...</div>
        ) : (
          <div>
            Error uploading file.
            <button type="button" onClick={() => setStatus("idle")}>
              Try Again
            </button>
          </div>
        )}
      </form>
    </div>
  );
}
