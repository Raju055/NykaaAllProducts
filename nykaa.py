import requests
import os
from bs4 import BeautifulSoup as soup
import json
import csv
from pathlib import Path



def func_create_folder(shade_path, product_path):
    Path(shade_path).mkdir(parents=True, exist_ok=True)
    Path(product_path).mkdir(parents=True, exist_ok=True)
    #Path.mkdir(product_path)




def func_save_img(shade_path, product_path, product_images, shade_images):
    try:
        i = 1
        for img in product_images:
            try:
                img_url = img
                img_url = img_url[:-7] + '1500_.jpg'
                full_path = product_path + '/_' + str(i) + '.jpg'
                with requests.get(img_url, stream=True) as r:
                    with open(full_path, "wb") as f:
                        f.write(r.content)
                i += 1
            except Exception:
                pass

        i = 1
        for img in shade_images:  # shade_dict = {"Shade Name": shade_name, "Shade Link": shade_link}
            try:
                img_name = img["Shade Name"]
                img_url = img.find('img')['Shade Link']
                img_url = img_url[:-7] + '1500_.jpg'
                full_path = shade_path + '_' + img_name + '.jpg'
                with requests.get(img_url, stream=True) as r:
                    with open(full_path, "wb") as f:
                        f.write(r.content)
                i += 1
            except Exception:
                pass
    except:
        pass



def func_product_details(root_dir, prod_page_soup, product_url, brand_category):
    try:
        product_images_count = ''

        product_images_count = 0
        product_images_src = []
        try:
            product_images = prod_page_soup.find("div", {"class": "slick-thumb"}).findAll("img")
            product_images_count = len(product_images)

            for img_url in product_images:
                try:
                    img_src = img_url["src"].replace("w-50", "w-620").replace("h-50", "h-620")
                    product_images_src.append(img_src)
                except:
                    pass
        except:
            pass

        product_name = prod_page_soup.find("h1", {"itemprop":"name"}).text.strip()

        # brand_category = brand_name

        # brand_category = prod_page_soup.findAll("ol", {"class": "breadcrumb product_des-breadcrumb"})

        rating = ''
        try:
            rating = ''
        except:
            pass
        descrtiptions = []
        try:
            desc_lst = prod_page_soup.findAll("div", {"class": "pdp-description-tab-item"})[0].findAll("p")
            for desc in desc_lst:
                descrtiptions.append(desc.text.strip())
        except:
            pass

        price = ''
        try:
            price =prod_page_soup.findAll("div", {"class":"price-info"})[-1].text.strip()[1:]
        except:
            pass

        top_reviews = []
        reviews = prod_page_soup.findAll("div", {"class":"review-content"})
        for review in reviews:
            top_reviews.append(review.text.strip())

        shade_images = []
        shade_img = prod_page_soup.findAll("span", {"class":"color-pallets  "})
        shade_img_count = len(shade_img)
        for img in shade_img:
            try:
                shade_name = img.find('img')['alt'].strip().split('-')[-1].strip()
                shade_link = img.find('img')['src']
                shade_dict = {"Shade Name": shade_name, "Shade Link": shade_link}
                shade_images.append(shade_dict)
            except:
                pass


        shade_path = root_dir +"/Nykaa Images/"+ brand_category +"/"+ product_name +"/Shades/"
        product_path = root_dir +"/Nykaa Images/"+ brand_category +"/"+ product_name

        column_values = [product_name, brand_category, price, rating, product_images_count,
                         shade_img_count, top_reviews, descrtiptions,  product_url]

        # columns = ["Product Name", "Brand Categoy", "Price", "Rating", "Product Images Count",
        #            "Shade Images Count", "Top Reviews", "Descriptions", "Product URL"]

        f = open(root_dir +"/naykaa_product_details.csv", "a", encoding="utf-8", newline="")
        csv_writer = csv.writer(f, delimiter=",")
        csv_writer.writerow(column_values)
        f.close()

        func_create_folder(shade_path, product_path)

        func_save_img(shade_path, product_path, product_images_src, shade_images)

    except:
        pass


def nykaa(root_dir):
    try:
        url = "https://www.nykaa.com/app-api/index.php/react/navigation?forDevice=desktop"

        req = requests.get(url)

        # Shade Image save with their name
        # columns = ["Product Images Count", "Product Name", "Brand Categoy", "Rating", "Product URL",
        #            "Price", "Top Reviews", "Shade Images Count"]


        columns = ["Product Name", "Brand Categoy", "Price", "Rating", "Product Images Count",
                   "Shade Images Count", "Top Reviews", "Descriptions", "Product URL"]

        f = open(root_dir +"/naykaa_product_details.csv", "w", encoding="utf-8", newline="")
        csv_writer = csv.writer(f, delimiter = ",")
        csv_writer.writerow(columns)
        f.close()

        page_data = req.text
        json_load = json.loads(page_data)
        #json_data = eval(str(req.text))

        brand_lst = list(json_load['brands'].keys())

        brands = json_load['brands']

        poduct_url_lst = []
        for brand in brand_lst:
            try:
                brand_lst_1 = brands[brand]

                for brand_detail in brand_lst_1:
                    try:
                        brand_id = brand_detail['brand_id']
                        brand_name = brand_detail['name']
                        brand_url_name = brand_name.replace("  ", " ").replace(" ", "-").lower()
                        x = "https://www.nykaa.com/"
                        # brands/maybelline-new-york/c/596?ptype=brand&id=596&root=brand_menu,top_brands,Maybelline New York
                        prod_url = x + "brands/"+ brand_url_name+"/c/" + str(brand_id) +"?ptype=brand&id="+ str(
                                brand_id) + "&root=brand_menu,top_brands,"+ brand_name
                        bran_dict = {"Name":brand_name, "url":prod_url}

                        poduct_url_lst.append(bran_dict)

                    except:
                        pass

            except:
                pass

            for brand_link in poduct_url_lst:
                try:
                    brand_url = brand_link["url"]
                    brand_category = brand_link["Name"].strip()

                    brand_req = requests.get(brand_url)
                    brand_soup = soup(brand_req.content, "html.parser")
                    no_of_pages = 1
                    one_page = True
                    try:
                        no_of_pages = brand_soup.find("span", {"class": "page-number"})
                        no_of_pages = int(no_of_pages.text.strip().split(" ")[-1].strip())
                    except:
                        pass

                    for pages_no in range(no_of_pages):
                        try:
                            if one_page == True:
                                brand_url = brand_url
                            else:
                                brand_url = brand_url + "&page_no=" + str(pages_no + 1)

                            one_page = False

                            # brand_soup = None
                            brand_req = 0
                            brand_req = requests.get(brand_url)
                            prod_soup = soup(brand_req.content, "html.parser")

                            product_url_lst = prod_soup.findAll("div", {"class": "tags-offer-container"})
                            for prod in product_url_lst:
                                try:
                                    product_url = "https://www.nykaa.com" + str(prod.nextSibling["href"])

                                    prod_req = requests.get(product_url)
                                    prod_page_soup = soup(prod_req.content, "html.parser")

                                    func_product_details(root_dir, prod_page_soup, product_url, brand_category)

                                except:
                                    pass

                        except:
                            pass

                except Exception as e:
                    print(e)
                    pass

    except:
        pass

if __name__ == '__main__':
    root_dir = os.path.dirname(os.path.abspath(__file__))
    nykaa(root_dir)