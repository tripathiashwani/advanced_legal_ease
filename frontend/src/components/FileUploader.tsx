const FileUploader = () => {
  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;
    const BASE_AUTH_URL = "http://127.0.0.1:8001/api/accounts/"

    const formData = new FormData();
    Array.from(files).forEach((file) =>
      formData.append("files", file)
    );

    await fetch(`${BASE_AUTH_URL}upload-pdf/`, {
      method: "POST",
      body: formData,
    });

    alert("PDF uploaded successfully");
  };

  return (
    <div>
      <input type="file" multiple accept="application/pdf" onChange={handleUpload} />
    </div>
  );
};

export default FileUploader;
