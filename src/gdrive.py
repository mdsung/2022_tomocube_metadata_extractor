from __future__ import print_function

import datetime
import io
import shutil
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]


class GDriveCredential:
    def __init__(self, scopes=SCOPES):
        self.scopes = scopes
        self.credentials = self.create_credentials()

    def create_credentials(self):
        credentials = None

        if Path("token.json").exists():
            credentials = self._parse_credentials()

        if not credentials or not credentials.valid:
            if (
                credentials
                and credentials.expired
                and credentials.refresh_token
            ):
                self._refresh_credentials(credentials)
            else:
                credentials = self._create_new_credentials()

            self._save_credentials(credentials, "token.json")

        return credentials

    def _parse_credentials(self, filename="token.json"):
        return Credentials.from_authorized_user_file(filename, self.scopes)

    def _refresh_credentials(self, credentials):
        credentials.refresh(Request())
        return credentials

    def _create_new_credentials(self):
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", self.scopes
        )
        return flow.run_local_server(port=0)

    def _save_credentials(self, credentials, filename: str):
        with open(filename, "w") as token:
            token.write(credentials.to_json())


class GDriveReader:
    def __init__(
        self,
        credentials,
        folder_id: str,
        folder: bool = False,
        image: bool = False,
    ):
        self.credentials = credentials
        self.folder_id = folder_id
        self.folder = folder
        self.image = image

    def read(self):
        page_token = None
        file_list: list[dict] = []
        query_str: str = f"'{self.folder_id}' in parents"

        if self.folder:
            query_str += " and mimeType = 'application/vnd.google-apps.folder'"

        if self.image:
            query_str += " and mimeType contains 'image/'"

        try:
            service = build("drive", "v3", credentials=self.credentials)

        except HttpError as error:
            print(f"An error occurred: {error}")

        else:
            while True:
                response = (
                    service.files()
                    .list(
                        q=query_str,
                        pageSize=100,
                        fields="*",
                        pageToken=page_token,
                    )
                    .execute()
                )

                for file in response.get("files", []):
                    one_file_dict = {
                        key: file[key]
                        for key in ["id", "name", "parents", "mimeType"]
                    }
                    file_list.append(one_file_dict)

                page_token = response.get("nextPageToken", None)

                if page_token is None:
                    break

        return file_list


class GDriveDownloader:
    pass


# def download_gdrive_file(self.creds, file_id, file_name):
#     service = build("drive", "v3", credentials=creds)

#     request = service.files().get_media(fileId=file_id)
#     fh = io.BytesIO()
#     downloader = MediaIoBaseDownload(fh, request)
#     done = False
#     while done is False:
#         status, done = downloader.next_chunk()
#         print(f"{file_name} Downloaded {int(status.progress() * 100):d}%")

#         fh.seek(0)
#         with open(Path(DATA_PATH, file_name), "wb") as f:
#             shutil.copyfileobj(fh, f)


def get_file_lists(creds, folder_id, folder=True):
    return _get_file_list(creds, folder_id, folder)


# def download_files(creds):
#     file_metadata = get_file_lists(creds)
#     for metadata in file_metadata:
#         if ("RI Tomogram" in metadata["name"]) & (
#             metadata["mimeType"] == "image/tiff"
#         ):
#             download_gdrive_file(creds, metadata["id"], metadata["name"])


class ImageType(Enum):
    BRIGHT_FIELD = auto()
    MIP = auto()
    RI_TOMOGRAM = auto()


@dataclass
class ImageFile:
    google_drive_file_id: str
    name: str
    project: str
    date: datetime.datetime
    cell_type: Optional[str] = None
    image_type: Optional[ImageType] = None
    status: Optional[str] = None  # patient subgroup

    @classmethod
    def from_metadata(cls, google_drive_file_id, name, project, date_time):
        return cls(google_drive_file_id, name, project, date_time)


def get_files_in_project(creds, project_folder: pd.Series) -> list[ImageFile]:
    folder_images: list[ImageFile] = []

    for date_folder in _get_file_list(creds, project_folder["id"], folder=True):
        for image in _get_file_list(creds, date_folder["id"], image=True):
            print(image)
            image_file: ImageFile = ImageFile.from_metadata(
                image["id"],
                image["name"],
                project_folder["name"],
                datetime.datetime.strptime(date_folder["name"], "%Y%m%d"),
            )
            folder_images.append(image_file)
    return folder_images
