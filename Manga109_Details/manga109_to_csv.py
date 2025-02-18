import os
import csv
import xml.etree.ElementTree as ET

import pandas as pd


def extract_details(annotation):
    id = annotation.get('id')
    xmin = int(annotation.get('xmin'))
    ymin = int(annotation.get('ymin'))
    xmax = int(annotation.get('xmax'))
    ymax = int(annotation.get('ymax'))
    x_center = (xmin + xmax) / 2
    y_center = (ymin + ymax) / 2
    width = xmax - xmin
    height = ymax - ymin
    area = width * height
    aspect_ratio = width / height

    return id, xmin, ymin, xmax, ymax, x_center, y_center, width, height, area, aspect_ratio

def determine_frame_id(x_center, y_center, frames):
    for frame in frames:
        frame_id, frame_xmin, frame_ymin, frame_xmax, frame_ymax = frame
        if frame_xmin <= x_center <= frame_xmax and frame_ymin <= y_center <= frame_ymax:
            return frame_id
    return None

# Function to normalize annotations
def normalize_annotations(annotations):
    annotations_normalized = annotations.copy()
    annotations_normalized.drop(['box_xmin', 'box_ymin', 'box_xmax', 'box_ymax', 'frame_id', 'text'], axis=1,
                                inplace=True)
    annotations_normalized['x_center'] /= 1654
    annotations_normalized['y_center'] /= 1170
    annotations_normalized['width'] /= 1654
    annotations_normalized['height'] /= 1170
    annotations_normalized['area'] /= 1654 * 1170

    return annotations_normalized

def parse_xml_to_csv(xml_folder, csv_file):
    if not os.path.exists(csv_file):
        with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['manga', 'page_index', 'type', 'id', 'box_xmin', 'box_ymin', 'box_xmax', 'box_ymax', 'x_center', 'y_center', 'width', 'height', 'area', 'aspect_ratio', 'frame_id', 'text'])

    rows = []
    for xml_file in os.listdir(xml_folder):
        if xml_file.endswith('.xml'):
            tree = ET.parse(os.path.join(xml_folder, xml_file))
            root = tree.getroot()
            manga_title = root.get('title')
            print(f"Processing manga: {manga_title}")

            for page in root.findall('pages/page'):
                page_index = page.get('index')
                page_has_annotations = False
                frames = []

                for frame in page.findall('frame'):
                    page_has_annotations = True
                    frame_id, frame_xmin, frame_ymin, frame_xmax, frame_ymax, x_center, y_center, width, height, area, aspect_ratio = extract_details(frame)
                    frames.append((frame_id, frame_xmin, frame_ymin, frame_xmax, frame_ymax))
                    rows.append([manga_title, page_index, 'frame', frame_id, frame_xmin, frame_ymin, frame_xmax, frame_ymax, x_center, y_center, width, height, area, aspect_ratio, None, None])

                for annotation_type in ['text', 'face', 'body']:
                    for annotation in page.findall(annotation_type):
                        page_has_annotations = True
                        annotation_id, xmin, ymin, xmax, ymax, x_center, y_center, width, height, area, aspect_ratio = extract_details(annotation)
                        text = annotation.text if annotation_type == 'text' else None
                        frame_id = determine_frame_id(x_center, y_center, frames)
                        rows.append([manga_title, page_index, annotation_type, annotation_id, xmin, ymin, xmax, ymax, x_center, y_center, width, height, area, aspect_ratio, frame_id, text])

                if not page_has_annotations:
                    rows.append([manga_title, page_index, None, None, None, None, None, None, None, None, None, None, None, None, None, None])

    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(rows)

def main():
    xml_folder = '../Manga109/annotations'
    csv_file_xml = '../Manga109/Manga109.csv'
    parse_xml_to_csv(xml_folder, csv_file_xml)

    annotations = pd.read_csv(csv_file_xml)
    processed_annotations = normalize_annotations(annotations)
    processed_annotations.to_csv('../Manga109/Manga109_processed.csv', index=False)

if __name__ == "__main__":
    main()