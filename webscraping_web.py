from flask import Flask, request, render_template, redirect, url_for
import webscraping_functions as wf

app = Flask(__name__)


@app.route('/', methods=['GET','POST'])
def main():
    if request.method == 'GET':
        return render_template('home.html')
    else:
        consola = request.form.get('consolas')
        juego = request.form['juego']
        tienda = request.form['tienda']
        print(tienda, consola, juego)
        return redirect("/search/"+tienda+"/"+consola+"/"+juego)


@app.route('/search/<tienda>/<consola>/<juego>')
def webscrap(tienda, consola, juego):
    
    if tienda == 'GAME':
        products = wf.GAME_webscraping(juego, consola, 10)
    elif tienda == 'FNAC':
        products = wf.FNAC_webscraping(juego, consola, 10)
    elif tienda == 'CARREFOUR':
        products = wf.CARREFOUR_webscraping(juego, consola, 10)

    products = img_to_img_src(products)

    return products.to_html(escape=False)


def img_to_img_src(df):
    df['p_imagen'] = ['<img src="'+ x +'">' for x in df['p_imagen']]
    return df

if __name__ == "__main__":
    app.run(debug=True)