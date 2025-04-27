"use client";
import { ChangeEvent, useState } from "react";

type UploadStatus = "idle" | "processing" | "success" | "error";

export default function UploadForm() {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [fastMode, setFastMode] = useState<boolean>(false);
  const [status, setStatus] = useState<UploadStatus>("idle");
  const [fileName, setFileName] = useState<string>("No file chosen");

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setFileName(e.target.files[0].name);
    } else {
      setFile(null);
      setFileName("No file chosen");
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
      const filename = `${language.toLowerCase()}.properties`;
      const link = document.createElement("a");
      link.href = downloadUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(downloadUrl);
      setStatus("success");
    } catch {
      setStatus("error");
    }
  }

  return (
    <div className="flex justify-center items-center min-h-screen">
      <div className="w-full max-w-md px-4">
        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label htmlFor="file" className="block text-2xl font-bold mb-2">
              File
            </label>
            <div className="border border-gray-300 rounded-lg overflow-hidden flex">
              <label
                htmlFor="fileInput"
                className="bg-gray-50 px-4 py-3 cursor-pointer border-r border-gray-300 text-lg"
              >
                Choose File
              </label>
              <div className="py-3 px-4 text-gray-500 text-lg">{fileName}</div>
              <input
                type="file"
                id="fileInput"
                onChange={handleFileChange}
                className="hidden"
              />
            </div>
          </div>

          <div className="mb-6">
            <label htmlFor="language" className="block text-2xl font-bold mb-2">
              Language
            </label>
            <input
              type="text"
              id="language"
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              placeholder="Enter language"
              className="w-full p-3 border border-gray-300 rounded-lg text-lg"
            />
          </div>

          <div className="mb-6">
            <label htmlFor="password" className="block text-2xl font-bold mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter password"
              className="w-full p-3 border border-gray-300 rounded-lg text-lg"
            />
          </div>

          <div className="mb-6 flex items-center">
            <input
              type="checkbox"
              id="fastMode"
              checked={fastMode}
              onChange={(e) => setFastMode(e.target.checked)}
              className="w-6 h-6 mr-2"
            />
            <label htmlFor="fastMode" className="text-xl font-bold">
              Fast Mode
            </label>
          </div>

          {status === "idle" || status === "success" ? (
            <button
              type="submit"
              className="w-full bg-blue-600 text-white py-3 rounded-lg text-xl"
            >
              Submit
            </button>
          ) : status === "processing" ? (
            <div className="w-full bg-blue-600 text-white py-3 rounded-lg text-xl text-center">
              Processing your upload...
            </div>
          ) : (
            <div className="text-center">
              <div className="mb-2">Error uploading file.</div>
              <button
                type="button"
                onClick={() => setStatus("idle")}
                className="w-full bg-blue-600 text-white py-3 rounded-lg text-xl"
              >
                Try Again
              </button>
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
