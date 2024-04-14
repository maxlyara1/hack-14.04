try:
    from io import BytesIO
    import pandas as pd
    import os
    import nltk
    from nltk.stem import SnowballStemmer
    import easyocr
    from PIL import Image, ImageDraw
    from io import BytesIO
    import streamlit as st
except Exception as e:
    print(e)


os.environ["KMP_DUPLICATE_LIB_OK"]="TRUE"

nltk.download('punkt')
nltk.download('stopwords')
stemmer = SnowballStemmer("russian")

black_list_marketing = [
    'без', 'без добавления', 'с низким содержанием', 'содержит только натуральные продукты',
     'обеспечивает одну из ваших пяти порций в день',
    'обеспечивает', 'содержит', 'натуральные', 'натурально', 'свежие', 'органические продукты',
    'натуральные фрукты', 'натуральные овощи', '100%', 'содержит три вида овощей',
    'сбалансированное питание', 'идеальный баланс витаминов', 'уникальный баланс минералов',
    'идеальный баланс минералов', 'уникальный баланс витаминов', 'идеальные питательные вещества',
    'обеспечивает надлежащее питание детей', 'содержит', 'является источником', 'полезно для',
    'поддерживает', 'улучшает', 'необходим для', 'здоровый', 'польза ', 'каша для детей',
    'сбалансировано', 'здоровое питание', 'сбалансированное', 'поддержка', 'восторг для ',
    'наполненные пользой', 'наполненные вкусом', 'приготовленные', 'на пару',
    'отобранные ингредиенты', 'специально отобранные ингредиенты',
    'к здоровью', 'вкусный',
    'вкуснятина', 'вкуснейший', 'подходит для', 'вострорг', 'вкусовая', 'любит', 'экзотические блюда',
    'вкус', 'разнообразие', 'простота вкуса', 'простота аромата', 'простота вкуса и аромата', 'нежная',
    'без комочков', 'легкая для глотания', 'специально разработана', 'идеальный первый прикорм ', 'удобно',
    'текстура', 'я с текстурой', 'просто для', 'отличный способ насладиться', 'ближе всего к домашней еде',
    'вдохновленный домашними рецептами', 'правильный выбор', 'обрести уверенность', 'получить удовольствие',
    'помочь', 'разработан ', 'разработано', 'выращенные', 'выращено',
    'ничего лишнего', 'никакой нездоровой пищи', 'ничего невкусного', 'способствует', 'гарантируем', 'гарант',
    'гарантия', 'совершенный', 'оптимальный', 'правительство рекомендует', 'воз', 'рекомендует',
    'министерство здравоохранения', 'минздрав', 'рекомендует', 'одобренное мамами', 'одобрено', '% прибыли', 'с каждой покупки', 'для',
    'маленьких', 'гурманов', 'гарантирую', 'natural', '200%', '300%', '400%', 'маленьких', 'гмо', 'уникальный', 'ингредиенты','пищеварение','гамма',
    'здоровье','развитие','здоровое','питание','отлично','специально','отобранные','сочные','обеспечивает','правильно','правильный','выбор','плодов','свежих',
    'из свежих','концентрата','консервантов','красителей','комфортное','в помощь','помощь', 'пребиотик','злаки','витамин','витаминов','доказано','мое первое','мой первый',
    'я гарантирую','для маленьких','сделано из','учимся','жевать','обогащено','полноценный','обед','с цельным','с цельной','с зерном','со злаками','по-домашнему','без крахмала', 'без гмо',
    'сахарин', 'ацесульфам', 'аспартам', 'сукралоза', 'стевия', 'никаких'
]

black_list_marketing = [stemmer.stem(word) for word in black_list_marketing]

# Initialize the OCR reader
reader = easyocr.Reader(['ru', 'en'])

# Function to draw boxes around words and highlight words from blacklist
def draw_boxes_with_blacklist(image, words_data_list, blacklist, width=3):
    draw = ImageDraw.Draw(image)
    badwords_list = []
    for word_data in words_data_list:
        word = word_data[1].lower()
        confidence = word_data[2]
        if len(word) > 1:
            splited_words = word.split()
            for a in splited_words:
                if stemmer.stem(a.lower()) in blacklist:
                    badwords_list.append(a)
                    p0, p1, p2, p3 = word_data[0]
                    draw.line([*p0, *p1, *p2, *p3, *p0], fill='red', width=6)
                elif confidence < 0.6:
                    p0, p1, p2, p3 = word_data[0]
                    draw.line([*p0, *p1, *p2, *p3, *p0], fill='orange', width=width)
                else:
                    p0, p1, p2, p3 = word_data[0]
                    draw.line([*p0, *p1, *p2, *p3, *p0], fill='green', width=width)
        else:
            if stemmer.stem(word.lower()) in blacklist:
                badwords_list.append(word)
                p0, p1, p2, p3 = word_data[0]
                draw.line([*p0, *p1, *p2, *p3, *p0], fill='red', width=6)
            elif confidence < 0.6:
                p0, p1, p2, p3 = word_data[0]
                draw.line([*p0, *p1, *p2, *p3, *p0], fill='orange', width=width)
            else:
                p0, p1, p2, p3 = word_data[0]
                draw.line([*p0, *p1, *p2, *p3, *p0], fill='green', width=width)

    return image, badwords_list

STYLE = """
<style>
img {
    max-width: 100%;
}
</style>
"""

class FileUpload(object):

    def __init__(self):
        self.fileTypes = ["png", "jpg"]

    def run(self):
        st.markdown(STYLE, unsafe_allow_html=True)

        # Adding a gif as background
        st.image("cat-meme.gif", use_column_width=True)

        files = st.file_uploader("Загрузить файл", type=self.fileTypes, accept_multiple_files=True)
        show_files = st.empty()
        if not files:
            show_files.info("Пожалуйста, загрузите файлы, формат которых: " + ", ".join(["png", "jpg"]))
            return None, None  # Return None for both contents and filenames

        contents = []
        filenames = []
        for file in files:
            content = file.getvalue()
            if isinstance(file, BytesIO):
                show_files.image(file)
                contents.append(content)
                filenames.append(file.name)
                # Save the image to the folder
                image_path = os.path.join("folder", file.name)
                with open(image_path, "wb") as f:
                    f.write(content)
            file.close()

        return contents, filenames

if __name__ == "__main__":
    # Create folder if it doesn't exist
    os.makedirs("folder", exist_ok=True)

    # Create an instance of the file upload class
    st.title("Проверка маркировки товара")

    st.info("Загрузите изображение для анализа:")

    file_upload = FileUpload()
    # Run the file upload and get the contents of the files
    image_contents, image_filenames = file_upload.run()

    if image_contents:

        for i, (image_content, image_filename) in enumerate(zip(image_contents, image_filenames)):
            review_text = ''
            email = ''
            st.write(f"Анализ изображения {i + 1}")
            
            image_path = os.path.join("folder", image_filename)

            st.write(f"Распознавание текста на изображении {i + 1}")
            result = reader.readtext(image_content, detail=1, paragraph=False)
            image = Image.open(BytesIO(image_content))
            annotated_image, badwords_result = draw_boxes_with_blacklist(image, result, black_list_marketing)
            result = badwords_result
            
            if len(result) >= 1:
                st.warning('Выявлены нарушения в маркировке или рекламе продукта')
                st.write("Выявленные нарушения:", result)
            else:
                st.success("Не выявлено нарушений в маркировке и рекламе продукта.")
            # Convert annotated image to bytes
            annotated_image_bytes = BytesIO()
            annotated_image.save(annotated_image_bytes, format='PNG')
            annotated_image_bytes.seek(0)  # Reset the file pointer to the beginning
            st.image(annotated_image_bytes, caption=f"Размеченное изображение {i + 1}", use_column_width=True)

            st.write("Если не согласен с результатом обработки фотографии")
            review_text = st.text_input(f"Краткий комментарий о выявленной ошибке:", key=f"review_text_{i}")
            email = st.text_input(f"Введите вашу почту:", key=f"email_{i}")
                                
            # Save data to log file
            log_file = "log.xlsx"
            if not os.path.exists(log_file):
                log_df = pd.DataFrame(columns=["Название файла", "Badwords", "Выявлены нарушения в маркировке или рекламе"])
                log_df.to_excel(log_file, index=False)  # Create an empty log file if it doesn't exist
            else:
                log_df = pd.read_excel(log_file)
            badwords = ', '.join(badwords_result) if badwords_result else None
            contains_multiple_badwords = len(badwords_result) >= 1
            new_row = {"Название файла": image_filename, "Badwords": badwords, 
                        "Выявлены нарушения в маркировке или рекламе": contains_multiple_badwords}
            log_df = pd.concat([log_df, pd.DataFrame([new_row])], ignore_index=True)
            log_df.to_excel(log_file, index=False)


            # Проверяем, были ли введены текст комментария и адрес электронной почты
            if review_text and email:
                if st.button(f"Отправить результат анализа {i + 1} на проверку администрации"):
                    # Сохраняем изображение в папку
                    annotated_image.save(image_path, format='PNG')

                    # Сохраняем данные об отзыве в Excel
                    review_data = {"Название файла": [image_filename], "Отзыв": [review_text], "Почта": [email]}
                    df = pd.DataFrame(review_data)
                    if os.path.exists("reviews.xlsx"):
                        existing_df = pd.read_excel("reviews.xlsx")
                        df = pd.concat([existing_df, df], ignore_index=True)
                    df.to_excel("reviews.xlsx", index=False)
                    st.success("Спасибо за замечание! Мы свяжемся после рассмотрения вашей заявки.")
