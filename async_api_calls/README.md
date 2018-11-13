Для локального запуска нужно создать файл `config.py`, содержащий строчку

```python
access_token = "your_secret_token"
```

Помимо этого, код `fetcher.py` написан под **Python 3.7**, который на момент написания не поставляется по дефолту в Анаконде, и поэтому для него нужно создать отдельное виртуальное окружение и поставить пакеты из `requirements.txt`

```bash
conda create -n py37 -c anaconda python=3.7
pip install -r requirements.txt
```
активировать его в терминале

```bash
source activate py37
```

и, собственно, запускать код `fetcher.py`
```bash
python fetcher.py
```
