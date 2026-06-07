import React from 'react'

export default function UploadSection({ onUpload, message }) {
  return (
    <div className="w-full rounded-2xl border border-[#333333] bg-[#111111] p-5 text-[#fff7b3]">
      <div className="mb-4">
        <h3 className="text-xl font-semibold text-[#fff7b3]">PDF Upload</h3>
        <p className="mt-2 text-sm text-[#b8ac6d]">Upload study files to keep your assistant aware of context (placeholder support).</p>
      </div>
      <div className="space-y-4">
        <input
          type="file"
          accept="application/pdf"
          className="w-full rounded-xl border border-[#333333] bg-[#101010] px-4 py-3 text-sm text-[#fff7b3] outline-none"
          onChange={(e) => onUpload && onUpload(e.target.files)}
        />
        <div className="rounded-xl border border-[#333333] bg-[#0b0b0b] p-4 text-sm text-[#b8ac6d]">
          {message}
        </div>
      </div>
    </div>
  )
}
