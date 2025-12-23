from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True permite que si cambias código, se actualice solo
    app.run(debug=True)