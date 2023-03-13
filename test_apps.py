from apps import *

def test_scraping_1(mocker):
    #configurar el mock
    mocker.patch("requests.get", return_value=0)
    html = download_data("https://www.fincaraiz.com.co/finca-raiz/venta/chapinero/bogota?pagina=1")
    assert html == 0
    
def test_scraping_2(mocker):
    assert f() != 200
    
def test_scraping_3(mocker):
    assert download_data("https://www.olx.com.co/carros_c378") != 200
