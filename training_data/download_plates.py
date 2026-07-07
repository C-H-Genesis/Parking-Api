from duckduckgo_search import DDGS
import requests
import os
import time
import hashlib

PLATE_CATEGORIES = {
    "eac/rwanda": [
        "Rwanda license plate",
        "Rwanda number plate car",
        "Rwanda vehicle registration plate",
        "plaque immatriculation Rwanda",
    ],
    "eac/tanzania": [
        "Tanzania license plate",
        "Tanzania number plate car",
        "Tanzania vehicle registration",
    ],
    "eac/kenya": [
        "Kenya license plate",
        "Kenya number plate car",
        "Kenya vehicle registration plate",
    ],
    "eac/uganda": [
        "Uganda license plate",
        "Uganda number plate car",
        "Uganda vehicle registration plate",
    ],
    "eac/burundi": [
        "Burundi license plate",
        "Burundi number plate car",
        "plaque immatriculation Burundi",
    ],
    "eac/south_sudan": [
        "South Sudan license plate",
        "South Sudan number plate car",
        "South Sudan vehicle registration",
    ],
    "eac/drc": [
        "Congo DRC license plate",
        "DRC number plate car",
        "plaque immatriculation Congo",
    ],
    "diplomatic/eu_delegation": [
        "European Union delegation vehicle plate Africa",
        "EU delegation license plate Rwanda",
        "EU mission vehicle plate Africa",
    ],
    "diplomatic/united_nations": [
        "United Nations UN vehicle plate Africa",
        "UN license plate Africa",
        "UNHCR UNDP vehicle plate Africa",
    ],
    "diplomatic/embassies": [
        "diplomatic CD license plate Africa",
        "corps diplomatique plate Africa",
        "embassy vehicle plate CD",
    ],
    "diplomatic/african_union": [
        "African Union vehicle plate",
        "AU mission license plate Africa",
    ],
    "diplomatic/other_orgs": [
        "international organization vehicle plate Africa",
        "NGO vehicle plate East Africa",
        "ICRC vehicle plate Africa",
    ],
    "special/government": [
        "Rwanda government vehicle plate",
        "East Africa government license plate",
        "official government car plate Africa",
    ],
    "special/military": [
        "military vehicle plate East Africa",
        "army vehicle plate Africa",
        "RDF military plate Rwanda",
    ],
    "special/police": [
        "police vehicle plate East Africa",
        "Rwanda National Police car plate",
        "police license plate Africa",
    ],
    "special/transit": [
        "transit license plate East Africa",
        "temporary vehicle plate Africa",
        "dealer plate East Africa",
    ],
}

BASE_DIR = os.path.join(os.path.dirname(__file__), "raw_photos")
IMAGES_PER_QUERY = 40


def download_image(url: str, filepath: str) -> bool:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200 and len(response.content) > 5000:
            with open(filepath, 'wb') as f:
                f.write(response.content)
            return True
    except Exception:
        pass
    return False


def download_category(folder: str, queries: list):
    target_dir = os.path.join(BASE_DIR, folder)
    os.makedirs(target_dir, exist_ok=True)

    print(f"\n{'='*50}")
    print(f"Downloading: {folder}")
    print(f"{'='*50}")

    downloaded = 0

    with DDGS() as ddgs:
        for query in queries:
            print(f"\n  Searching: '{query}'")
            try:
                results = list(ddgs.images(
                    query,
                    max_results=IMAGES_PER_QUERY,
                    type_image="photo"
                ))

                for result in results:
                    url = result.get("image", "")
                    if not url:
                        continue

                    # Use hash of URL as filename to avoid duplicates
                    ext = url.split('.')[-1].split('?')[0].lower()
                    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
                        ext = 'jpg'
                    filename = hashlib.md5(url.encode()).hexdigest()[
                        :12] + f".{ext}"
                    filepath = os.path.join(target_dir, filename)

                    if os.path.exists(filepath):
                        continue

                    if download_image(url, filepath):
                        downloaded += 1
                        print(f"  ✓ {downloaded} images", end='\r')

                    time.sleep(0.3)  # be polite to servers

            except Exception as e:
                print(f"  Error: {e}")
                continue

    total = len([f for f in os.listdir(target_dir)
                 if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))])
    print(f"\n  Total in {folder}: {total} images")
    return total


def main():
    print("Starting plate image download...")
    print(f"Saving to: {BASE_DIR}\n")

    grand_total = 0
    total_categories = len(PLATE_CATEGORIES)

    for i, (folder, queries) in enumerate(PLATE_CATEGORIES.items(), 1):
        print(f"[{i}/{total_categories}] {folder}")
        count = download_category(folder, queries)
        grand_total += count
        time.sleep(2)  # pause between categories

    print("\n" + "="*50)
    print("DOWNLOAD SUMMARY")
    print("="*50)
    for folder in PLATE_CATEGORIES:
        target_dir = os.path.join(BASE_DIR, folder)
        if os.path.exists(target_dir):
            count = len([f for f in os.listdir(target_dir)
                        if f.endswith(('.jpg', '.jpeg', '.png', '.webp'))])
            print(f"  {folder}: {count} images")

    print(f"\nTotal images downloaded: {grand_total}")


if __name__ == "__main__":
    main()
