import { useState } from "react";
import "../styles/Fileupload.css";

function FileUpload() {

  const [file, setFile] = useState(null);
  const [students, setStudents] = useState([]);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);

  // =========================
  // Upload Excel
  // =========================

  const handleUpload = async () => {

    if (!file) {
      alert("Please select an Excel file");
      return;
    }

    setLoading(true);

    const formData = new FormData();

    formData.append("file", file);

    // Custom AI instruction
    formData.append(
      "prompt",
      prompt
    );

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.error || "Upload failed"
        );
      }

      setStudents(
        data.data || []
      );

      alert(
        data.message ||
        "Excel uploaded successfully"
      );

    } catch (error) {

      console.error(
        "Upload Error:",
        error
      );

      alert(
        error.message ||
        "Upload Failed"
      );

    } finally {

      setLoading(false);

    }
  };


  // =========================
  // Find Phone Number
  // =========================

  const getPhoneNumber = (student) => {

    return (
      student.NUMBER ||
      student.PHONE ||
      student.PHONE_NUMBER ||
      student.MOBILE ||
      student.MOBILE_NUMBER ||
      student.CONTACT ||
      student.CONTACT_NUMBER ||
      ""
    );
  };


  // =========================
  // Send Single WhatsApp
  // =========================

  const sendWhatsApp = async (student) => {

    const phone = getPhoneNumber(student);

    if (!phone) {
      alert(
        "Phone number not found for this record"
      );
      return;
    }

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/send-whatsapp",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            phone: String(phone),
            message: student.message,
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.error ||
          "Message sending failed"
        );
      }

      alert(
        data.message
      );

    } catch (error) {

      console.error(
        "WhatsApp Error:",
        error
      );

      alert(
        error.message ||
        "WhatsApp Send Failed"
      );

    }
  };


  // =========================
  // Send All Messages
  // =========================

  const sendAllMessages = async () => {

    if (students.length === 0) {

      alert(
        "No messages available"
      );

      return;
    }

    setSending(true);

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/send-all",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            students: students,
          }),
        }
      );

      const data =
        await response.json();

      if (!response.ok || !data.success) {
        throw new Error(
          data.error ||
          "Bulk sending failed"
        );
      }

      alert(
        `Done! ${data.sent} messages sent successfully.`
      );

    } catch (error) {

      console.error(
        "Bulk Send Error:",
        error
      );

      alert(
        error.message ||
        "Bulk Send Failed"
      );

    } finally {

      setSending(false);

    }
  };


  // =========================
  // Render
  // =========================

  return (

    <section className="upload-section">

      <div className="upload-card">

        <h2>
          Upload Excel File
        </h2>

        <p>
          Upload your dataset and let AI
          generate personalized WhatsApp
          messages automatically.
        </p>


        {/* ========================= */}
        {/* AI Prompt */}
        {/* ========================= */}

        <div className="prompt-section">

          <label>
            AI Message Instructions
          </label>

          <textarea
            className="prompt-input"
            placeholder="Example: Create a friendly reminder for the client based on the information in the Excel row."
            value={prompt}
            onChange={(e) =>
              setPrompt(e.target.value)
            }
            rows="5"
          />

          <small>
            Leave this empty to let NotifyX
            automatically generate a relevant
            message from the Excel data.
          </small>

        </div>


        {/* ========================= */}
        {/* Upload Box */}
        {/* ========================= */}

        <div className="upload-box">

          <span>
            📊
          </span>

          <h3>
            Drag & Drop Excel File
          </h3>

          <p>
            .xlsx and .xls supported
          </p>

          <input
            type="file"
            accept=".xlsx,.xls"
            onChange={(e) =>
              setFile(
                e.target.files[0]
              )
            }
          />

          {file && (

            <p className="selected-file">
              Selected: {file.name}
            </p>

          )}

          <button
            className="upload-btn"
            onClick={handleUpload}
            disabled={loading}
          >

            {loading
              ? "🤖 Generating Messages..."
              : "📤 Upload & Generate"
            }

          </button>

        </div>


        {/* ========================= */}
        {/* Generated Messages */}
        {/* ========================= */}

        {students.length > 0 && (

          <div className="preview-section">

            <h2>
              Generated Messages
            </h2>


            {/* Send All */}

            <button
              className="send-all-btn"
              onClick={sendAllMessages}
              disabled={sending}
            >

              {sending
                ? "📤 Sending Messages..."
                : "📤 Send All Messages"
              }

            </button>


            {/* Message Cards */}

            {students.map(
              (student, index) => {

                const phone =
                  getPhoneNumber(
                    student
                  );

                // Hide phone-number columns
                // from the visible data list

                const visibleFields =
                  Object.entries(
                    student
                  ).filter(
                    ([key]) =>
                      key.toLowerCase() !==
                        "message" &&
                      ![
                        "number",
                        "phone",
                        "phone_number",
                        "mobile",
                        "mobile_number",
                        "contact",
                        "contact_number"
                      ].includes(
                        key.toLowerCase()
                      )
                  );


                return (

                  <div
                    key={index}
                    className="message-card"
                  >

                    {/* Record Header */}

                    <h3>
                      Record #{index + 1}
                    </h3>


                    {/* Data */}

                    <div className="record-data">

                      {visibleFields.map(
                        ([key, value]) => (

                          <p
                            key={key}
                          >

                            <strong>
                              {key}:
                            </strong>{" "}

                            {String(
                              value
                            )}

                          </p>

                        )
                      )}

                    </div>


                    {/* Phone */}

                    <p>

                      <strong>
                        Number:
                      </strong>{" "}

                      {phone || "Not Found"}

                    </p>


                    {/* AI Message */}

                    <div className="generated-message">

                      <strong>
                        AI Generated Message:
                      </strong>

                      <pre>
                        {student.message}
                      </pre>

                    </div>


                    {/* Single Send */}

                    <button
                      className="send-btn"
                      onClick={() =>
                        sendWhatsApp(
                          student
                        )
                      }
                    >

                      📲 Send WhatsApp

                    </button>

                  </div>

                );

              }
            )}

          </div>

        )}

      </div>

    </section>

  );

}

export default FileUpload;