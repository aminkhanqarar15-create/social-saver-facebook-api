from flask import Flask, request, jsonify, send_from_directory
import yt_dlp
import os
import uuid

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)


@app.route("/")
def home():
    return jsonify({
        "success": True,
        "message": "Social Saver Pro API is running"
    })


@app.route("/download", methods=["POST"])
def download():

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "No data received"
        }), 400

    url = str(data.get("url", "")).strip()

    if not url:
        return jsonify({
            "success": False,
            "message": "Facebook URL is required"
        }), 400

    lower_url = url.lower()

    if (
        "facebook.com" not in lower_url
        and "fb.watch" not in lower_url
        and "fb.com" not in lower_url
    ):
        return jsonify({
            "success": False,
            "message": "Invalid Facebook URL"
        }), 400

    filename = str(uuid.uuid4()) + ".mp4"

    output_path = os.path.join(
        DOWNLOAD_FOLDER,
        filename
    )

    options = {
        "quiet": True,
        "no_warnings": True,

        "format":
            "best[ext=mp4][acodec!=none][vcodec!=none]"
            "/best[ext=mp4]"
            "/best",

        "outtmpl": output_path,

        "merge_output_format": "mp4",

        "noplaylist": True,

        "retries": 3,

        "socket_timeout": 60
    }

    try:

        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=True
            )

        if not os.path.exists(output_path):

            files = os.listdir(
                DOWNLOAD_FOLDER
            )

            mp4_files = [
                f for f in files
                if f.endswith(".mp4")
            ]

            if mp4_files:

                latest = max(
                    mp4_files,
                    key=lambda f:
                    os.path.getmtime(
                        os.path.join(
                            DOWNLOAD_FOLDER,
                            f
                        )
                    )
                )

                filename = latest

        if not os.path.exists(
            os.path.join(
                DOWNLOAD_FOLDER,
                filename
            )
        ):

            return jsonify({
                "success": False,
                "message": "Video file was not created"
            }), 500

        return jsonify({

            "success": True,

            "title": info.get(
                "title",
                "Facebook Video"
            ),

            "download_url":
                "/files/" + filename

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500


@app.route("/files/<filename>")
def files(filename):

    return send_from_directory(
        DOWNLOAD_FOLDER,
        filename,
        as_attachment=True
    )


if __name__ == "__main__":

    port = int(
        os.environ.get(
            "PORT",
            5000
        )
    )

    app.run(
        host="0.0.0.0",
        port=port
    )
