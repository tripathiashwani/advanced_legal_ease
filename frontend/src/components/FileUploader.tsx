const FileUploader = () => {
  const handleUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;

    // 🔗 Send files to backend for PDF embedding
    console.log("Uploaded PDFs:", files);
  };

  return (
    <div>
      <label className="block text-sm font-medium mb-2">
        Upload Case Documents (PDF)
      </label>
      <input
        type="file"
        accept="application/pdf"
        multiple
        onChange={handleUpload}
        className="block w-full text-sm"
      />
    </div>
  );
};

export default FileUploader;
