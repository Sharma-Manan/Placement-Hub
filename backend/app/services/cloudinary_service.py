import cloudinary.uploader

class CloudinaryService:

    @staticmethod
    def upload_image(file, folder: str = "profile_photos"):
        try:
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                resource_type="image"
            )

            return {
                "url": result.get("secure_url"),
                "public_id": result.get("public_id")
            }

        except Exception as e:
            raise Exception(f"Cloudinary upload failed: {str(e)}")

    @staticmethod
    def delete_image(public_id: str):
        try:
            cloudinary.uploader.destroy(public_id)
        except Exception:
            pass  # don't break flow if delete fails