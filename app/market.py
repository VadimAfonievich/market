from market_class import Market
from tqdm import tqdm
from categories import categories
from categories import proxy
import json
import os
import requests
import random
import re
import uuid
import datetime
import shutil
import zipfile
import time
import multiprocessing


def timed(func):
	"""
	records approximate durations of function calls
	"""
	def wrapper(*args, **kwargs):
		start = time.time()
		print('{name:<30} started'.format(name=func.__name__))
		result = func(*args, **kwargs)
		duration = "{name:<30} finished in {elapsed:.2f} seconds".format(
			name=func.__name__, elapsed=time.time() - start
		)
		print(duration)
		return result
	return wrapper


class MarketService:

	proxies = []

	def __init__(self, proxies=[]) -> None:
		self.proxies = proxies
		pass

	def clean(self, value):
		return value.replace("'", "`").replace("\\", "").replace("\n", "\\r\\n")

	# @timed
	def save_result(self, item, folder, sale_price):
		try:
			# item = result[0]
			# folder = result[1]
			# sale_price = result[2]
			done = False

			if not os.path.exists(f"items/{folder}/images"):
				os.mkdir(f"items/{folder}/images")
			if not os.path.exists(f"items/{folder}/images/images1"):
				os.mkdir(f"items/{folder}/images/images1")
			if not os.path.exists(f"items/{folder}/images/images2"):
				os.mkdir(f"items/{folder}/images/images2")
			out_cat_folder_1 = f"items/{folder}/images/images1/{item['out_cat_id']}"
			out_cat_folder_2 = f"items/{folder}/images/images2/{item['out_cat_id']}"
			if not os.path.exists(out_cat_folder_1):
				os.mkdir(out_cat_folder_1)
			if not os.path.exists(out_cat_folder_2):
				os.mkdir(out_cat_folder_2)
			product_image1_folder = f"items/{folder}/images/images1/{item['out_cat_id']}/{item['id']}"
			product_image2_folder = f"items/{folder}/images/images2/{item['out_cat_id']}/{item['id']}"
			if not os.path.exists(product_image1_folder):
				os.mkdir(product_image1_folder)
			if not os.path.exists(product_image2_folder):
				os.mkdir(product_image2_folder)

			if sale_price == 1:
				discount = random.randint(1, 3)
				sale_price = int(int(item['price']) * (100 - discount)/100)

				i = 0
				for image in item['images']:
					r = requests.get(
						"https:" + image.replace("https:", "").replace("http:", "").replace("1hq", "orig").replace("50x50",
																												   "orig"))
					image_file1 = f"{product_image1_folder}/{item['id']}_{i}.jpg"
					if not os.path.exists(image_file1):
						with open(image_file1, "wb") as f:
							f.write(r.content)
					image_file2 = f"{product_image2_folder}/{uuid.uuid4()}.jpg"
					if not os.path.exists(image_file2):
						with open(image_file2, "wb") as f:
							f.write(r.content)
					i += 1

			else:
				sale_price = 0
				i = 0
				for image in item['images']:
					r = requests.get(
						"https:" + image.replace("https:", "").replace("http:", "").replace("1hq", "orig").replace("50x50",
																												   "orig"))
					image_file1 = f"{product_image1_folder}/{item['id']}_{i}.jpg"
					if not os.path.exists(image_file1):
						with open(image_file1, "wb") as f:
							f.write(r.content)
					i += 1

			folder_images_path = f"items/{folder}/images"
			zip_file_name = 'img.zip'
			output_directory = f"items/{folder}"

			with zipfile.ZipFile(os.path.join(output_directory, zip_file_name), "w", zipfile.ZIP_DEFLATED) as zip_file:
				root_path = os.path.dirname(folder_images_path)
				for root, dirs, files in os.walk(folder_images_path):
					for file in files:
						file_path = os.path.join(root, file)
						relative_path = os.path.relpath(file_path, root_path)
						zip_file.write(file_path, arcname=relative_path)

			query_file = f"items/{folder}/queries/{item['out_cat_id']}.sql"
			if not os.path.exists(query_file):
				with open(query_file, "wt", encoding='utf-8') as f:
					f.write(f"SET @categoryID = {item['out_cat_id']};\n")

			with open(query_file, "at", encoding='utf-8') as f:
				f.write(f"CALL insert_product({item['price']}, {sale_price}, '{self.clean(item['name'])}', "
						f"'{self.clean(item['brand_name'])}', '{self.clean(item['model'])}', '{self.clean(item['desc'])}');\n")

				for spec in item['specs']:
					for sp in spec['attrs']:
						f.write(f"CALL insert_attribute('{self.clean(item['brand_name'])}', '{self.clean(item['model'])}', '{self.clean(sp['label'])}', '{self.clean(sp['value'])}');\n")

				try:
					i = 0
					for image in item['images']:
						f.write(f"CALL insert_image({item['id']}, '{self.clean(item['brand_name'])}', '{self.clean(item['model'])}', '{item['id']}_{i}.jpg');\n")
						i += 1
				except:
					pass

				try:
					for key, value in item['reviews'].items():
						f.write(f"CALL insert_review('{self.clean(item['brand_name'])}', '{self.clean(item['model'])}', '{self.clean(key)}', '{self.clean(value['rating'])}', '{self.clean(value['date'])}', '{self.clean(value['positive_comment'])}', '{self.clean(value['negative_comment'])}', '{self.clean(value['comment'])}');\n")
				except:
					pass

			folder_sql_path = f"items/{folder}/queries"
			zip_file_name = "sql.zip"
			output_directory = f"items/{folder}"

			with zipfile.ZipFile(os.path.join(output_directory, zip_file_name), "w", zipfile.ZIP_DEFLATED) as zip_file:
				root_path = os.path.dirname(folder_sql_path)
				for root, dirs, files in os.walk(folder_sql_path):
					for file in files:
						file_path = os.path.join(root, file)
						relative_path = os.path.relpath(file_path, root_path)
						zip_file.write(file_path, arcname=relative_path)

			done = True
			return done
		except:
			pass

	def prepare_result(self, folder):
		main_folder = f"items/{folder}"
		queries_folder = f"items/{folder}/queries"
		images_folder = f"items/{folder}/images"
		if not os.path.exists(main_folder):
			os.mkdir(main_folder)
		if not os.path.exists(queries_folder):
			os.mkdir(queries_folder)
		if not os.path.exists(images_folder):
			os.mkdir(images_folder)

	def process(self, inputs):
		for input in inputs:
			category_url = input[0]
			out_cat_id = input[1]
			max_items = input[2]
			sale_price = input[3]
			category_id = re.match(r".*?/(\d+)/?", category_url).group(1)
			print(f"category_url: {category_url} \nid: {out_cat_id} \nmax_items: {max_items} \ncategory_id: {category_id}\n")

			if not category_id:
				print("Error, bad category url")
				continue
			
			category_folder = "items/categories"
			category_json = f"{category_folder}/{category_id}.json"
			if not os.path.exists(category_folder):
				os.mkdir(category_folder)

			short_items = self.parse_category(category_id, max_items, out_cat_id)
			with open(category_json, 'wt', encoding='utf-8') as fp:
				fp.write(json.dumps(short_items))

			print(f"\nВсего объявлений к парсингу (max_items): {max_items} \n")
			# Уникализируем по id элемента
			short_items = list({v['id']: v for v in short_items}.values())
			full_items = self.parse_items(short_items, out_cat_id, sale_price)

			print("Сохранение json, sql, images...")

			for item in full_items:
				self.save_result(item, out_cat_id, sale_price)

			# pool = multiprocessing.Pool(processes=5)
			#
			# result = [(item, out_cat_id, sale_price) for item in full_items]
			# results = pool.map(self.save_result, result)
			#
			# pool.close()
			# pool.join()

			# shutil.rmtree(f"items/{out_cat_id}/images")
			# shutil.rmtree(f"items/{out_cat_id}/queries")

			end_time = datetime.datetime.now()
			work_time = end_time - start_time
			print(f"ГОТОВО!Все результаты сохранены!\n"
				  # f"Парсинг занял: {work_time}\n\n"
				  f"{end_time}\n"
				  f"===========================================================================")

	def get_proxy(self):
		if len(self.proxies) > 0:
			return self.proxies[0]
		else:
			return None

	# @timed
	def parse_category(self, category_id, max_items, out_cat_id):
		self.prepare_result(out_cat_id)

		short_items = []
		# mkt = Market(proxy=self.get_proxy())
		page = 1
		count = 0
		while True:
			while True:
				city = mkt.set_location()
				# print(city)

				content = mkt.get_category_by_id(category_id, page)
				next_page = mkt.parse_next_page_category(content)
				items = mkt.parse_products_from_html(content)
				if len(items) == 0:
					# print(content)
					with open("category_error.html", "wt", encoding='utf-8') as f:
						f.write(content)
				else:
					break
					#exit()
			# print(items)
			for item in items:
				short_items.append(item)

			# Уникализируем по id элемента
			short_items = list({v['id']: v for v in short_items}.values())
			count = len(short_items)

			if next_page:
				page = next_page
			else:
				break
			if count >= max_items:
				break
		# обрезаем до max_items
		short_items = short_items[:max_items]
		return short_items

	# @timed
	def parse_items(self, items, out_cat_id, sale_price):
		# mkt = Market(proxy=self.get_proxy())
		full_items = []
		i = 0
		n = 0

		for i, item in tqdm(enumerate(items), total=len(items), dynamic_ncols=True):
			i += 1
			# print(f"Прогресс: {i}/{len(items)}", end="\r")
			# print(f"Объявление № {i}")
			no_price = True
			if os.path.exists(f"./items/{item['id']}.json"):
				with open(f"./items/{item['id']}.json", "rt") as fp:
					item = json.loads(fp.read())
					if not item['price']:
						no_price = True
					else:
						no_price = False
						full_items.append(item)
						n += 1
						# print("Уже имеется!")

			if no_price:
				item['out_cat_id'] = out_cat_id

				content = mkt.get_product_by_id(item['id'])

				brand = mkt.parse_product_brand(content)
				item['brand_name'] = brand

				images = mkt.parse_product_images(content)
				item['images'] = images

				price = mkt.parse_product_price(content)

				if price:
					item['price'] = price

				content = mkt.get_product_specs_by_id(item['id'])
				it = mkt.parse_specs(content)
				item['specs'] = it['attributes'] if 'attributes' in it else ''
				item['desc'] = it['desc'] if 'desc' in it else ''

				review_content = mkt.get_product_reviews_by_id(item['id'])
				reviews = mkt.parse_reviews(review_content)
				item['reviews'] = reviews

				model_content = mkt.get_model_name_dy_id(item['id'])
				model_name = mkt.parse_model_name(model_content)
				item['model'] = model_name

				full_items.append(item)
				# print(f"=> id: {item['id']} / brand_name: {item['brand_name']} / price: {item['price']} / images: {item['images']}")

				with open(f"./items/{item['id']}.json", "wt") as fp:
					json.dump(item, fp)

		print(f"\n===========================================================================\n"
			  f"Пройдено объявлений: {i}\n"
			  f"Уже имелось объявлений: {n}\n"
			  f"НОВЫХ объявлений: {i - n}\n")

		return full_items

# proxy = 'akparov3397:750c14@162.19.196.77:11287'
# ms = MarketService(proxies=[proxy])

# proxy = '42000936db:f390601021@192.162.57.253:26828'
# proxy = 'c64d3da0f2:31af12e6d3@5.101.5.122:63684'

start_time = datetime.datetime.now()
print(f"Начало работы: \n{start_time} \nСТАРТ!\n")

try:
	with Market(proxy=proxy) as mkt:
		ms = MarketService(proxies=[proxy])
		ms.process(categories)
except KeyboardInterrupt:
	pass
except Exception as ex:
	print(f"{ex}")
	pass
finally:
	pass
