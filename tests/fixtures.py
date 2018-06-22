"""
Copyright 2018 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import json


gif_response = json.loads("""{
  "results": [
    {
      "created": 1520636640.424062,
      "url": "https://tenor.com/VDng.gif",
      "media": [
        {
          "nanomp4": {
            "url": "https://media.tenor.com/videos/0cb9dfebd15018a5c41c4b09e38f4603/mp4",
            "dims": [
              76,
              40
            ],
            "duration": 8.933333,
            "preview": "https://media.tenor.com/images/731e5fe36ee192422482edea66fc9620/tenor.png",
            "size": 68508
          },
          "nanowebm": {
            "url": "https://media.tenor.com/videos/3810dce6869fe053a733a94da6bbfe76/webm",
            "dims": [
              76,
              40
            ],
            "preview": "https://media.tenor.com/images/731e5fe36ee192422482edea66fc9620/tenor.png",
            "size": 73978
          },
          "tinygif": {
            "url": "https://media.tenor.com/images/6dae491b16b00707e0658c568b93bdab/tenor.gif",
            "dims": [
              220,
              118
            ],
            "preview": "https://media.tenor.com/images/9caf27374675050d737a36b7095ee2c3/tenor.gif",
            "size": 456504
          },
          "tinymp4": {
            "url": "https://media.tenor.com/videos/d406e80cb3498626f6021205051feb2b/mp4",
            "dims": [
              166,
              88
            ],
            "duration": 8.933333,
            "preview": "https://media.tenor.com/images/f3ed024334277a6d9222d9d8013b8780/tenor.png",
            "size": 166950
          },
          "tinywebm": {
            "url": "https://media.tenor.com/videos/8e0b912e941d221deefa2d86de201969/webm",
            "dims": [
              166,
              88
            ],
            "preview": "https://media.tenor.com/images/f3ed024334277a6d9222d9d8013b8780/tenor.png",
            "size": 217640
          },
          "webm": {
            "url": "https://media.tenor.com/videos/d6ced731c3461d084e057421efb81fe0/webm",
            "dims": [
              416,
              224
            ],
            "preview": "https://media.tenor.com/images/1b7446613a50219636b4299992e6daf0/tenor.png",
            "size": 237925
          },
          "gif": {
            "url": "https://media.tenor.com/images/ad84b1269b576e0d87b74a8adc09295c/tenor.gif",
            "dims": [
              416,
              224
            ],
            "preview": "https://media.tenor.com/images/1b7446613a50219636b4299992e6daf0/tenor.png",
            "size": 7655329
          },
          "mp4": {
            "url": "https://media.tenor.com/videos/1a99850da5f5b278d394e0da3667828a/mp4",
            "dims": [
              416,
              224
            ],
            "duration": 8.933333,
            "preview": "https://media.tenor.com/images/1b7446613a50219636b4299992e6daf0/tenor.png",
            "size": 396737
          },
          "nanogif": {
            "url": "https://media.tenor.com/images/39cc928d325dd3ee6ab9089121ed97a0/tenor.gif",
            "dims": [
              167,
              90
            ],
            "preview": "https://media.tenor.com/images/216fb17dd2fb92d860eaecac97626741/tenor.gif",
            "size": 281852
          },
          "mediumgif": {
            "url": "https://media.tenor.com/images/989f5142a249e25c776e3d47682a8bd9/tenor.gif",
            "dims": [
              416,
              224
            ],
            "preview": "https://media.tenor.com/images/2a14201ce0f5aeaa27b0a1803255e9fd/tenor.gif",
            "size": 1981318
          },
          "loopedmp4": {
            "url": "https://media.tenor.com/videos/afb6f589849a2dc12a7af58905f222b1/mp4",
            "dims": [
              416,
              224
            ],
            "duration": 26.801302,
            "preview": "https://media.tenor.com/images/1b7446613a50219636b4299992e6daf0/tenor.png",
            "size": 1188713
          }
        }
      ],
      "tags": [],
      "shares": 1,
      "itemurl": "https://tenor.com/view/office-space-dancing-break-dance-celebrate-gangsta-gif-11313704",
      "composite": null,
      "hasaudio": false,
      "title": "",
      "id": "11313704"
    }
  ],
  "next": "0"
}""")  # noqa: E501


empty_gif_response = json.loads("""{
  "results": [],
  "next": "0"
}""")
