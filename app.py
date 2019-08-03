import swapi
from flask import Flask, render_template, request
from requests import get

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():
    # Initialize the context
    context = {"found": False, "search": False}
    qp_term = request.args.get('search_term')
    if request.method == "POST" or qp_term:
        # If a multiple was found, then we need to grab from the query parameter
        # Did you say ‘ex-leper’?
        if qp_term:
            term = qp_term
        else:
            # Grab the client's search term from form
            term = request.form["search_term"]
        # The helper library doesn't have a search function so we'll make the request ourselves.
        search_response = get(f"https://swapi.co/api/people/?search={term}").json()
        count = search_response["count"]

        # Only one result returned. That’s right, sir. 16 years behind a veil and proud of it, sir.
        if count == 1:
            person = search_response["results"][0]
            planet = int("".join(n for n in person["homeworld"] if n.isdigit()))
            homeworld = swapi.get_planet(planet)
            # Population can be a number or "unknown"
            try:
                population = "{0:,d}".format(int(homeworld.population))
            except ValueError:
                population = homeworld.population.title()
            # Create content response to send back to client
            context = {
                "search": True,
                "found": True,
                "name": person["name"],
                "homeworld_name": homeworld.name,
                "homeworld_population": population,
                "homeworld_climate": homeworld.climate,
            }
        # Multiple results returned
        elif 1 < count:
            # Send list of found names to the client
            results = list()
            for r in search_response["results"]:
                results.append(r["name"])
            context = {
                "found": True,
                "search": True,
                "name": term,
                "multiples": results,
                "multiples_count": len(results),
            }
        # No results returned
        elif count < 1:
            context = {"found": False, "search": True, "name": term}

    return render_template("index.html", context=context)


if __name__ == "__main__":
    app.run()
