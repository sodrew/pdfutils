import json
import os
import sys
import fitz

def load_config(config_file):
    try:
        with open(config_file, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_file}' not found.")
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in configuration file '{config_file}'.")
    return None



def get_pdf_file(config_file, entry_file):
    pdf_file = os.path.join(os.path.dirname(config_file), entry_file)
    if not os.path.exists(pdf_file):
        print(f"Error: PDF file '{pdf_file}' does not exist.")
        return None
    return pdf_file

def is_file_type(filename, extensions):
    extension = os.path.splitext(filename)[1].lower()
    return extension in extensions

def is_image_file(filename):
    return is_file_type(filename, ['.png', '.jpg', '.jpeg', '.gif', '.bmp'])

def convert_image_to_pdf(image, image_file):
    # Get the dimensions of the image
    pdfbytes = image.convert_to_pdf()
    tmp = fitz.open("pdf", pdfbytes)
    page = tmp.load_page(0)
    width = page.rect.width
    height = page.rect.height
    tmp.close()

    # Create a new PDF document
    pdf = fitz.open()
    pdf.name = image_file

    # Get the dimensions of a standard letter page
    page_width, page_height = fitz.paper_size("letter")

    # Create a new page in the PDF document with letter page dimensions
    page = pdf.new_page(width=page_width, height=page_height)

    # Calculate the scaling factors for the image
    scale_x = page_width / width
    scale_y = page_height / height
    scale = min(scale_x, scale_y)

    # Calculate the new dimensions of the scaled image
    new_width = int(width * scale)
    new_height = int(height * scale)

    # Calculate the position to center the image on the page
    x = (page_width - new_width) / 2
    y = (page_height - new_height) / 2

    # Create an image annotation and insert the scaled IMAGE image
    rect = fitz.Rect(x, y, x + new_width, y + new_height)
    page.insert_image(rect, filename=image_file, keep_proportion=True)

    # Close the IMAGE object
    image.close()

    return pdf

def get_pages_to_extract(entry, pdf):
    pages_to_extract = entry.get('extract')
    if not pages_to_extract:
        pages_to_extract = list(range(1, pdf.page_count + 1))

    if not isinstance(pages_to_extract, list):
        print(f"Error: 'extract' value for entry must be a list of page numbers.")
        return None

    # Convert page numbers to 0-based index
    pages_to_extract = [page_num - 1 for page_num in pages_to_extract]

    # Check if the specified pages exist
    invalid_pages = [page_num for page_num in pages_to_extract if page_num < 0 or page_num >= pdf.page_count]
    if invalid_pages:
        print(f"Error: Attempting to operate on invalid page(s): {invalid_pages} in '{pdf_file}'.")
        return None

    return pages_to_extract


def redact_page(page, keywords):
    counter = 0
    for keyword in keywords:
        text_instances = page.search_for(keyword)
        for inst in text_instances:
            # Create a redaction annotation for each instance of the keyword
            annot = page.add_redact_annot(inst)

            # Apply the redaction by setting the overlay color
            annot.set_colors(stroke=None, fill=(0, 0, 0))

            # Apply the redaction to the page content
            page.apply_redactions()

            counter += 1
    print("\tRedaction(s):", counter)


def add_watermark(pdf, watermark_info):

    if not watermark_info:
        return
    if len(watermark_info) == 2:
        watermark_info.append(1)
        watermark_info.append([0,0])

    wm_file, wm_pages, wm_ratio, [wm_off_x, wm_off_y] = watermark_info

    watermark_image = None
    watermark_pdf = None
    if is_image_file(wm_file):
        # Create a watermark object from the image file
        watermark_image = fitz.Pixmap(wm_file)
        watermark_width = watermark_image.width
        watermark_height = watermark_image.height
    elif is_file_type(wm_file, ['.pdf']):
        watermark_pdf = fitz.open(wm_file)
        watermark_width, watermark_height = watermark_pdf.load_page(0).mediabox_size
    else:
        print('error: unknown type of watermark; not added')
        return

    # Iterate over each page of the PDF
    for page_num in wm_pages:
        page = pdf.load_page(page_num - 1)

        # fix upside down watermarks
        if not page.is_wrapped:
            page.wrap_contents()

        overflow = False
        if wm_off_x + watermark_width * wm_ratio > page.rect.width:
            watermark_width = page.rect.width - wm_off_x
            overflow = True
        if wm_off_y + watermark_height * wm_ratio > page.rect.height:
            watermark_height = page.rect.height - wm_off_y
            overflow = True

        if overflow:
            print("\tWatermark overflowing contents on page: {page_num}")

        watermark_rect = fitz.Rect(wm_off_x, wm_off_y,
                                   wm_off_x + watermark_width * wm_ratio,
                                   wm_off_y + watermark_height * wm_ratio)

        page.show_pdf_page(watermark_rect,  # cover the full page
                           watermark_pdf,  # the PDF with the watermark
                           0,  # choose page number in 'src'
                           keep_proportion=True,  # like before: stretch
            )

    print("\tWatermark added")

def process_pdf_entry(pdf, output_pdf,
                      pages_to_extract, redact_keywords, watermark_info,
                      rotate):
    # Print information about the file being processed
    print("Processing file:", pdf.name)
    print("\tPages to extract:", [page_num + 1 for page_num in pages_to_extract])
    print("\tKeywords to redact:", redact_keywords or None)

    for page_num in pages_to_extract:
        page = pdf.load_page(page_num)
        if rotate > 0:
            page.set_rotation(rotate)
        if redact_keywords:
            redact_page(page, redact_keywords)
        add_watermark(pdf, watermark_info)
        output_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)

def process_entries(config_file):
    # Load the configuration file
    config_data = load_config(config_file)
    if config_data is None:
        return

    # Extract configuration values
    global_redact_keywords = config_data.get('redact', [])
    encrypt_pwd = config_data.get('encrypt')
    output_file = config_data.get('output', 'output.pdf')

    # Create a list to store the extracted PDF file paths
    extracted_pdfs = []

    # Create a new PDF document for the concatenated output
    output_pdf = fitz.open()

    # Iterate through each PDF entry in the configuration file
    for entry in config_data.get('pdfs', []):
        if entry.get('encrypt'):
            print(f"Error: Invalid JSON format in configuration file '{config_file}'; encrypt should be outside of input files.")
            exit(-1)

        rotate = entry.get('rotate', 0)


        pdf_file = get_pdf_file(config_file, entry['file'])
        if pdf_file is None:
            continue

        # Open the PDF file
        pdf = fitz.open(pdf_file)

        redact_keywords = None
        # if this is an image file bypass most processing
        if is_image_file(pdf_file):
            pdf = convert_image_to_pdf(pdf, pdf_file)
        else:
            # Get the redact keywords for the current entry
            redact_keywords = set(global_redact_keywords)
            entry_redact_keywords = entry.get('redact')
            if entry_redact_keywords:
                redact_keywords.update(entry_redact_keywords)

        # Get the pages to extract
        pages_to_extract = get_pages_to_extract(entry, pdf)
        if pages_to_extract is None:
            pdf.close()
            continue

        # Get the watermark; filename and page are mandatory
        watermark_info = entry.get('watermark', [])
        if watermark_info and len(watermark_info) > 0:
            if len(watermark_info) in [2,4]:
                watermark_info[0] = get_pdf_file(config_file,
                                             watermark_info[0])
            else:
                print('Error: invalid watermark params')

        # Process the PDF entry
        process_pdf_entry(pdf, output_pdf,
                          pages_to_extract, redact_keywords,
                          watermark_info, rotate)

        # Close the PDF file
        pdf.close()

        print("\n")

    if len(output_pdf) == 0:
        print('Error: No pages to output')
        exit(-1)

    # Save the concatenated output PDF
    output_pdf_path = os.path.join(os.path.dirname(config_file), output_file)
    # Encrypt the output PDF with a password if specified
    if encrypt_pwd:
        perm = int(
            # Ensure everyone with the PDF can access it
            fitz.PDF_PERM_ACCESSIBILITY
            | fitz.PDF_PERM_PRINT # permits printing
            | fitz.PDF_PERM_COPY # permits copying
            | fitz.PDF_PERM_ANNOTATE # permits annotations
        )

        output_pdf.save(output_pdf_path,
                        encryption=fitz.PDF_ENCRYPT_AES_256,
                        user_pw=encrypt_pwd,
                        permissions=perm)
    else:
        output_pdf.save(output_pdf_path)

    # Close the file
    output_pdf.close()

    print("Output PDF saved:", output_pdf_path)
    if encrypt_pwd:
        print("\tEncrypted with password:", encrypt_pwd)

    # Remove the temporary PDF files
    for extracted_pdf_path in extracted_pdfs:
        os.remove(extracted_pdf_path)


def find_config_file(directory):
    config_file_name = 'config.json'
    current_dir = os.path.abspath(directory)

    while True:
        config_file_path = os.path.join(current_dir, config_file_name)
        if os.path.isfile(config_file_path):
            return config_file_path

        # Move up one directory level
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            # Reached the root directory, config file not found
            return None
        current_dir = parent_dir

def main():
    # Check if the directory or config file path is provided as a command-line argument
    if len(sys.argv) < 2:
        print("Please provide the directory or path to the configuration file as a command-line argument.")
    else:
        arg = sys.argv[1]
        config_file = None

        # Check if the argument is a directory
        if os.path.isdir(arg):
            config_file = find_config_file(arg)
            if config_file is None:
                print("Error: No 'config.json' file found in the specified directory.")
                return
        else:
            config_file = arg

        process_entries(config_file)


if __name__ == '__main__':
    main()
