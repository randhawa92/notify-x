from flask import Flask, request, jsonify
from flask_cors import CORS

from services.ai_service import generate_message
from services.whatsapp import send_whatsapp

import os
import time
import pandas as pd


# =========================================================
# APP CONFIGURATION
# =========================================================

app = Flask(__name__)

CORS(app)

UPLOAD_FOLDER = "uploads"

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)


# =========================================================
# PHONE COLUMN NAMES
# =========================================================

PHONE_COLUMNS = [
    "NUMBER",
    "PHONE",
    "PHONE_NUMBER",
    "MOBILE",
    "MOBILE_NUMBER",
    "CONTACT",
    "CONTACT_NUMBER"
]


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "NotifyX Backend is running 🚀"
    })


# =========================================================
# FIND PHONE COLUMN
# =========================================================

def find_phone_column(columns):

    for column in columns:

        if (
            str(column)
            .strip()
            .upper()
            in PHONE_COLUMNS
        ):
            return column

    return None


# =========================================================
# GET PHONE FROM RECORD
# =========================================================

def get_phone_number(row):

    for key, value in row.items():

        if (
            str(key)
            .strip()
            .upper()
            in PHONE_COLUMNS
        ):

            if (
                value is not None
                and str(value).strip() != ""
            ):
                return str(value).strip()

    return ""


# =========================================================
# UPLOAD EXCEL
# =========================================================

@app.route(
    "/upload",
    methods=["POST"]
)
def upload_file():

    try:

        # -------------------------------------------------
        # CHECK FILE
        # -------------------------------------------------

        if "file" not in request.files:

            return jsonify({
                "success": False,
                "error": "No Excel file uploaded."
            }), 400


        file = request.files["file"]


        if file.filename == "":

            return jsonify({
                "success": False,
                "error": "No file selected."
            }), 400


        # -------------------------------------------------
        # FILE TYPE
        # -------------------------------------------------

        extension = os.path.splitext(
            file.filename
        )[1].lower()


        if extension not in [
            ".xlsx",
            ".xls"
        ]:

            return jsonify({
                "success": False,
                "error": (
                    "Only .xlsx and .xls "
                    "files are supported."
                )
            }), 400


        # -------------------------------------------------
        # SAVE FILE
        # -------------------------------------------------

        filepath = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        file.save(filepath)


        print("\n===================================")
        print("          NOTIFYX EXCEL")
        print("===================================")
        print(
            "File:",
            file.filename
        )


        # -------------------------------------------------
        # READ EXCEL
        # -------------------------------------------------

        df = pd.read_excel(
            filepath
        )


        # -------------------------------------------------
        # CLEAN DATA
        # -------------------------------------------------

        df = df.dropna(
            how="all"
        )

        df.columns = (
            df.columns
            .astype(str)
            .str.strip()
        )

        df = df.fillna("")


        # -------------------------------------------------
        # EMPTY FILE CHECK
        # -------------------------------------------------

        if df.empty:

            return jsonify({
                "success": False,
                "error": (
                    "The Excel file contains "
                    "no usable records."
                )
            }), 400


        # -------------------------------------------------
        # PHONE COLUMN
        # -------------------------------------------------

        phone_column = find_phone_column(
            df.columns
        )


        if phone_column is None:

            return jsonify({
                "success": False,
                "error": (
                    "Phone number column not found. "
                    "Use NUMBER, PHONE, PHONE_NUMBER, "
                    "MOBILE or CONTACT."
                )
            }), 400


        print(
            "Phone Column:",
            phone_column
        )


        # -------------------------------------------------
        # AI INSTRUCTION
        # -------------------------------------------------

        custom_instruction = (
            request.form
            .get("prompt", "")
            .strip()
        )


        if not custom_instruction:

            custom_instruction = (
                "Create a personalized, professional "
                "and relevant WhatsApp message based "
                "only on the information provided in "
                "the Excel row. Do not invent information."
            )


        # -------------------------------------------------
        # EXCEL → RECORDS
        # -------------------------------------------------

        records = df.to_dict(
            orient="records"
        )


        final_data = []


        # -------------------------------------------------
        # GENERATE AI MESSAGES
        # -------------------------------------------------

        for index, row in enumerate(records):

            print(
                f"Generating message "
                f"{index + 1}/{len(records)}..."
            )


            try:

                message = generate_message(
                    row,
                    custom_instruction
                )

                row["message"] = message

                final_data.append(
                    row
                )

                print(
                    "AI Message Generated ✅"
                )


            except Exception as e:

                print(
                    "AI Generation Error:",
                    e
                )

                row["message"] = (
                    "Hello,\n\n"
                    "We wanted to share an "
                    "important update with you.\n\n"
                    "Please contact us if you "
                    "have any questions.\n\n"
                    "Regards,\n"
                    "NotifyX"
                )

                final_data.append(
                    row
                )


        # -------------------------------------------------
        # RESPONSE
        # -------------------------------------------------

        print("\n===================================")
        print(
            "AI Message Generation Completed"
        )
        print(
            "Records:",
            len(final_data)
        )
        print("===================================\n")


        return jsonify({

            "success": True,

            "message": (
                f"{len(final_data)} records processed "
                "and AI messages generated successfully."
            ),

            "filename": file.filename,

            "phone_column": phone_column,

            "total_records": len(final_data),

            "data": final_data

        })


    except Exception as e:

        print(
            "Upload Error:",
            e
        )

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =========================================================
# SEND SINGLE WHATSAPP
# =========================================================

@app.route(
    "/send-whatsapp",
    methods=["POST"]
)
def whatsapp_send():

    try:

        data = request.get_json(
            silent=True
        )


        if not data:

            return jsonify({
                "success": False,
                "error": (
                    "No message data received."
                )
            }), 400


        phone = str(
            data.get(
                "phone",
                ""
            )
        ).strip()


        message = str(
            data.get(
                "message",
                ""
            )
        ).strip()


        if not phone:

            return jsonify({
                "success": False,
                "error": (
                    "Phone number is missing."
                )
            }), 400


        if not message:

            return jsonify({
                "success": False,
                "error": (
                    "Message is empty."
                )
            }), 400


        print("\n===================================")
        print(
            "       NOTIFYX WHATSAPP"
        )
        print("===================================")
        print(
            "Recipient:",
            phone
        )


        # -------------------------------------------------
        # ACTUAL WHATSAPP SERVICE
        # -------------------------------------------------

        result = send_whatsapp(
            phone,
            message
        )


        if result:

            print(
                "Status: SENT ✅"
            )

            return jsonify({

                "success": True,

                "status": "sent",

                "message": (
                    "WhatsApp message sent successfully."
                )

            })


        print(
            "Status: FAILED ❌"
        )


        return jsonify({

            "success": False,

            "status": "failed",

            "error": (
                "WhatsApp message could not be sent."
            )

        }), 500


    except Exception as e:

        print(
            "WhatsApp Error:",
            e
        )

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =========================================================
# SEND ALL WHATSAPP MESSAGES
# =========================================================

@app.route(
    "/send-all",
    methods=["POST"]
)
def send_all():

    try:

        request_data = request.get_json(
            silent=True
        )


        if not request_data:

            return jsonify({
                "success": False,
                "error": (
                    "No data received."
                )
            }), 400


        records = request_data.get(
            "students",
            []
        )


        if not isinstance(
            records,
            list
        ):

            return jsonify({
                "success": False,
                "error": (
                    "Invalid records data."
                )
            }), 400


        if len(records) == 0:

            return jsonify({
                "success": False,
                "error": (
                    "No messages available to send."
                )
            }), 400


        total = len(records)

        sent_count = 0
        failed_count = 0

        results = []


        print("\n===================================")
        print(
            "       NOTIFYX SEND ALL"
        )
        print("===================================")
        print(
            "Total:",
            total
        )
        print("===================================\n")


        # -------------------------------------------------
        # SEND ONE BY ONE
        # -------------------------------------------------

        for index, row in enumerate(records):

            try:

                phone = get_phone_number(
                    row
                )


                message = str(
                    row.get(
                        "message",
                        ""
                    )
                ).strip()


                # -----------------------------------------
                # PHONE VALIDATION
                # -----------------------------------------

                if not phone:

                    failed_count += 1

                    results.append({

                        "index": index,

                        "status": "failed",

                        "error": (
                            "Phone number not found."
                        )

                    })

                    continue


                # -----------------------------------------
                # MESSAGE VALIDATION
                # -----------------------------------------

                if not message:

                    failed_count += 1

                    results.append({

                        "index": index,

                        "phone": phone,

                        "status": "failed",

                        "error": (
                            "Message is empty."
                        )

                    })

                    continue


                print(
                    f"Sending "
                    f"{index + 1}/{total} "
                    f"→ {phone}"
                )


                # -----------------------------------------
                # SEND
                # -----------------------------------------

                success = send_whatsapp(
                    phone,
                    message
                )


                if success:

                    sent_count += 1

                    results.append({

                        "index": index,

                        "phone": phone,

                        "status": "sent"

                    })

                    print(
                        "Status: SENT ✅"
                    )


                else:

                    failed_count += 1

                    results.append({

                        "index": index,

                        "phone": phone,

                        "status": "failed",

                        "error": (
                            "WhatsApp sending failed."
                        )

                    })

                    print(
                        "Status: FAILED ❌"
                    )


                # -------------------------------------------------
                # SMALL PROCESSING DELAY
                # -------------------------------------------------

                time.sleep(2)


            except Exception as e:

                failed_count += 1

                print(
                    f"Record "
                    f"{index + 1} Error:",
                    e
                )


                results.append({

                    "index": index,

                    "status": "failed",

                    "error": str(e)

                })


        # -------------------------------------------------
        # FINAL RESULT
        # -------------------------------------------------

        print("\n===================================")
        print(
            "NotifyX Send All Completed"
        )
        print(
            "Sent:",
            sent_count
        )
        print(
            "Failed:",
            failed_count
        )
        print(
            "Total:",
            total
        )
        print("===================================\n")


        return jsonify({

            "success": True,

            "message": (
                f"{sent_count} of {total} "
                "messages processed."
            ),

            "sent": sent_count,

            "failed": failed_count,

            "total": total,

            "results": results

        })


    except Exception as e:

        print(
            "Bulk Send Error:",
            e
        )

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# =========================================================
# RUN NOTIFYX
# =========================================================

if __name__ == "__main__":

    print("\n===================================")
    print("          NOTIFYX BACKEND")
    print("===================================")
    print(
        "Server: http://127.0.0.1:5000"
    )
    print(
        "Status: Running 🚀"
    )
    print("===================================\n")


    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )