import urllib.request
import xml.etree.ElementTree as ET

SOURCE_FEED_URL = "https://feed-p.topnlab.ru/export/database/bWxxR0VyWE9adHBvdUwvSQ,,/feed.xml"
COMPANY_NAME = "Самолет Плюс Красногорск"
WEBSITE_URL = "https://yandex.ru"

req = urllib.request.Request(SOURCE_FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=40) as response:
    xml_content = response.read()

root = ET.fromstring(xml_content)

yml_catalog = ET.Element("yml_catalog", date=root.attrib.get("generation-date", ""))
shop = ET.SubElement(yml_catalog, "shop")

ET.SubElement(shop, "name").text = COMPANY_NAME
ET.SubElement(shop, "company").text = COMPANY_NAME
ET.SubElement(shop, "url").text = WEBSITE_URL

currencies = ET.SubElement(shop, "currencies")
ET.SubElement(currencies, "currency", id="RUR", rate="1")

categories = ET.SubElement(shop, "categories")
ET.SubElement(categories, "category", id="1").text = "Квартиры"

offers = ET.SubElement(shop, "offers")
ns = {"y": "http://webmaster.yandex.ru/schemas/feed/realty/2010-06"}

for offer in root.findall("y:offer", ns):
    offer_id = offer.attrib.get("internal-id", "")
    rooms = offer.findtext("y:rooms", default="", namespaces=ns)
    area = offer.findtext("y:area/y:value", default="", namespaces=ns)
    price = offer.findtext("y:price/y:value", default="0", namespaces=ns)
    locality = offer.findtext("y:location/y:locality-name", default="Красногорск", namespaces=ns)
    address = offer.findtext("y:location/y:address", default="", namespaces=ns)
    description = offer.findtext("y:description", default="", namespaces=ns)

    room_label = f"{rooms}-к квартира" if rooms else "Квартира"
    name_title = f"{room_label}, {area} м², {locality}"

    yml_offer = ET.SubElement(offers, "offer", id=offer_id, available="true")
    ET.SubElement(yml_offer, "name").text = name_title
    try:
        ET.SubElement(yml_offer, "price").text = str(int(float(price)))
    except (ValueError, TypeError):
        ET.SubElement(yml_offer, "price").text = "0"

    ET.SubElement(yml_offer, "currencyId").text = "RUR"
    ET.SubElement(yml_offer, "categoryId").text = "1"

    url_elem = offer.findtext("y:url", default=WEBSITE_URL, namespaces=ns)
    ET.SubElement(yml_offer, "url").text = url_elem

    for img in offer.findall("y:image", ns):
        if img.text:
            ET.SubElement(yml_offer, "picture").text = img.text

    full_desc = f"{address}. {description}".strip()
    ET.SubElement(yml_offer, "description").text = full_desc[:2900]

    if area:
        p_area = ET.SubElement(yml_offer, "param", name="Общая площадь")
        p_area.text = f"{area} м²"
    if address:
        p_addr = ET.SubElement(yml_offer, "param", name="Адрес")
        p_addr.text = address

tree = ET.ElementTree(yml_catalog)
ET.indent(tree, space="  ", level=0)
tree.write("feed.xml", encoding="utf-8", xml_declaration=True)
print("Файл feed.xml успешно сгенерирован!")
