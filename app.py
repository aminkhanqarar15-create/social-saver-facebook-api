from flask import Flask, request, jsonify
import yt_dlp

app = Flask(__name__)


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

    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "format": "best[ext=mp4]/best"
    }

    try:

        with yt_dlp.YoutubeDL(options) as ydl:

            info = ydl.extract_info(
                url,
                download=False
            )

            video_url = info.get("url")

            if not video_url:

                formats = info.get("formats", [])

                for fmt in reversed(formats):

                    if fmt.get("url"):
                        video_url = fmt["url"]
                        break

            if not video_url:
                return jsonify({
                    "success": False,
                    "message": "Video URL not found"
                }), 404

            return jsonify({
                "success": True,
                "title": info.get(
                    "title",
                    "Facebook Video"
                ),
                "download_url": video_url
            })

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000
    )
