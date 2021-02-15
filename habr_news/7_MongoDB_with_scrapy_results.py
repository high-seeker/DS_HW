# -----Импорт пакетов-------------------------------------------------------------
import pprint
from pymongo import MongoClient
import json


# -----Подключение----------------------------------------------------------------

# установить соединение с MongoClient
client = MongoClient(host='localhost', port=27017)
print(f"client: {client}\n")

# удалить БД (каждый раз начинаем "с чистого листа")
client.drop_database('habr_news')

# создать БД
db = client['habr_news']
print(f"db: {db}\n")

# создать коллекцию
collection = db.habr_news_collection
print(f"collection: {collection}\n")

# ------Добавление------------------------------------------------------------------------------------------------------

# загрузить json полученный в результате работы scrapy
with open('./habr_news/habr_news.json') as json_file:
    habr_news = json.load(json_file)

# добавить все данные из json в mongodb
insert_many_result = db.habr_news_collection.insert_many(habr_news)
print(f"db.habr_news_collection.insert_many(many_posts):\n"
      f"\ttype = {type(insert_many_result)}\n"
      f"\tvalue = {insert_many_result}\n")
many_post_ids = insert_many_result.inserted_ids
print(f"db.habr_news_collection.insert_many(many_posts).inserted_ids:\n"
      f"\ttype = {type(many_post_ids)}\n"
      f"\tvalue_count = {len(many_post_ids)}\n")

# ------Запросы---------------------------------------------------------------------------------------------------------

# количество документов в коллекции
print(f"db.habr_news_collection.count_documents({{}}): {db.habr_news_collection.count_documents({})}\n")

# получить имена коллекций из БД
print(f"db.list_collection_names(): {db.list_collection_names()}\n")

# получить один любой документ из коллекции
print(f"db.list_collection_names.find_one():\n"
      f"{pprint.pformat(db.list_collection_names.find_one())}\n")

# получить один документ из коллекции удовлетворяющий условию {'news_id': 529690}
print(f"db.habr_news_collection.find_one({{'name': Авито}}):\n"
      f"{pprint.pformat(db.habr_news_collection.find_one({'news_id': 529690}))}\n")

# получить все документы из коллекции удовлетворяющие условию {'comments_counter': 3} + сортировка по 'news_id'
print(f"db.habr_news_collection.find({{'comments_counter': 3}}):")
for doc in db.habr_news_collection.find({'comments_counter': 3}).sort("news_id"):
    print(f"name: {doc['name']}\tinfo: {doc['info']}")

# получить все документы из коллекции удовлетворяющие условию {'author': 'avouner'}
print(f"\ndb.habr_news_collection.find({{'author': 'avouner'}}):")
for doc in db.habr_news_collection.find({'author': 'avouner'}):
    print(f"name: {doc['name']}\tinfo: {doc['info']}")

# получить количество документов из коллекции поле tags которых содержит `Научно-популярное` (другие теги тоже допустимы)
print(f"\ndb.habr_news_collection.count_documents({{'tags': {{'$all': ['Научно-популярное']}}}}): "
      f"{db.habr_news_collection.count_documents({'tags': {'$all': ['Научно-популярное']}})}\n")

# ------Обновление------------------------------------------------------------------------------------------------------

# установить в качестве `author` имя `MONGO`
# во всех документах удовлетворяющие условию {'hubs': {'$all': ['Астрономия']}}
# и получить количество обновленных
update_many_result = db.habr_news_collection.update_many({'tags': {'$all': ['Астрономия']}},
                                                              {'$set': {'author': 'MONGO'}})
print(f"\ndb.habr_news_collection.update_many({{'tags': {{'$all': ['Астрономия']}}}},"
      f"{{'$set': {{'author': 'MONGO'}}}}:")
many_matched_count = update_many_result.matched_count
print(f"many_matched_count\ntype = {type(many_matched_count)}\n"
      f"value = {many_matched_count}\n")
many_modified_count = update_many_result.modified_count
print(f"many_modified_count\ntype = {type(many_modified_count)}\n"
      f"value = {many_modified_count}\n")

# получить количество документов из коллекции, в которых 'author' = 'MONGO'
print(f"db.habr_news_collection.count_documents({{'author': 'MONGO'}}): "
      f"{db.habr_news_collection.count_documents({'author': 'MONGO'})}")

# ------Удаление--------------------------------------------------------------------------------------------------------

# удалить все документы, у которых 'comments_counter' равен 0
# и получить количество удаленных
delete_many_result = db.habr_news_collection.delete_many({'comments_counter': 0})
print(f"delete_many_result:\n"
      f"\ttype = {type(delete_many_result)}\n"
      f"\tvalue = {delete_many_result}\n")
many_deleted_count = delete_many_result.deleted_count
print(f"many_deleted_count:\n"
      f"\ttype = {type(many_deleted_count)}\n"
      f"\tvalue = {many_deleted_count}\n")