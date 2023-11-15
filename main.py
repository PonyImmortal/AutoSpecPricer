import os
from flask import Flask, request, redirect, url_for, render_template, send_from_directory, flash
from update_compare_save import update_and_process_file, compare_and_save

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}
PRICE_FILENAME = 'price_file.xlsx'
SPEC_FILENAME = 'spec_file.xlsx'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'supersecretkey'


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(uploaded_file, target_filename):
    if uploaded_file and allowed_file(uploaded_file.filename):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], target_filename)
        uploaded_file.save(filepath)
        return True
    return False


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        files_saved = False

        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        if save_uploaded_file(request.files.get('price_file', None), PRICE_FILENAME):
            flash('Файл прайса успешно сохранен!', 'success')
            files_saved = True

        if save_uploaded_file(request.files.get('spec_file', None), SPEC_FILENAME):
            flash('Файл спецификации успешно сохранен!', 'success')
            files_saved = True

        if not files_saved:
            flash('Ошибка! Убедитесь, что вы загружаете правильные файлы.', 'error')

    return render_template('upload.html')


@app.route('/update_and_process')
def update_and_process():
    try:
        update_and_process_file(PRICE_FILENAME)
        flash('Прайс успешно преобразован!', 'success')
    except Exception as e:
        flash(f'Ошибка при преобразовании прайса: {e}', 'error')
    return redirect(url_for('upload_file'))


@app.route('/compare')
def compare():
    try:
        compare_and_save(PRICE_FILENAME, SPEC_FILENAME)
        flash('Сравнение выполнено успешно!', 'success')
    except Exception as e:
        flash(f'Ошибка при сравнении файлов: {e}', 'error')
    return redirect(url_for('upload_file'))


@app.route('/download')
def download_file():
    path = os.path.join(UPLOAD_FOLDER, "compared_price.xlsx")
    return send_from_directory(os.path.dirname(path), os.path.basename(path), as_attachment=True)


if __name__ == '__main__':
    app.run(debug=True)
