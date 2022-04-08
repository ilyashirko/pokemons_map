import folium


from django.http import HttpResponseNotFound, HttpRequest
from django.shortcuts import render
from pokemon_entities.models import Pokemon, PokemonEntity




MOSCOW_CENTER = [55.751244, 37.618423]
DEFAULT_IMAGE_URL = (
    'https://vignette.wikia.nocookie.net/pokemon/images/6/6e/%21.png/revision'
    '/latest/fixed-aspect-ratio-down/width/240/height/240?cb=20130525215832'
    '&fill=transparent'
)


def add_pokemon(folium_map, lat, lon, image_url=DEFAULT_IMAGE_URL):
    icon = folium.features.CustomIcon(
        image_url,
        icon_size=(50, 50),
    )
    folium.Marker(
        [lat, lon],
        # Warning! `tooltip` attribute is disabled intentionally
        # to fix strange folium cyrillic encoding bug
        icon=icon,
    ).add_to(folium_map)


def show_all_pokemons(request):
    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for entity in PokemonEntity.objects.all():
        add_pokemon(
            folium_map,
            entity.latitude,
            entity.longitude,
            f'media/{entity.pokemon.image}'
        )

    pokemons_on_page = []
    for pokemon in Pokemon.objects.all():
        pokemons_on_page.append({
            'pokemon_id': pokemon.id,
            'img_url': f'{HttpRequest.build_absolute_uri(request, f"/media/{pokemon.image}")}',
            'title_ru': pokemon.title,
        })

    return render(request, 'mainpage.html', context={
        'map': folium_map._repr_html_(),
        'pokemons': pokemons_on_page,
    })


def show_pokemon(request, pokemon_id):
    try:
        requested_pokemon = Pokemon.objects.get(id=pokemon_id)
    except AttributeError:
        return HttpResponseNotFound('<h1>Такой покемон не найден</h1>')

    pokemon = {
        "pokemon_id": requested_pokemon.id,
        "title_ru": requested_pokemon.title,
        "title_en": requested_pokemon.title_en,
        "title_jp": requested_pokemon.title_jp,
        "img_url": f'{HttpRequest.build_absolute_uri(request, f"/media/{requested_pokemon.image}")}',
        "description": requested_pokemon.description,
    }

    if requested_pokemon.evolution:
        pokemon.update({
            "next_evolution": {
                "title_ru": requested_pokemon.evolution.title,
                "pokemon_id": requested_pokemon.evolution.id,
                "img_url": f'{HttpRequest.build_absolute_uri(request, f"/media/{requested_pokemon.evolution.image}")}'
            }
        })
    
    if requested_pokemon.deevolution:
        pokemon.update({
            "next_evolution": {
                "title_ru": requested_pokemon.deevolution.title,
                "pokemon_id": requested_pokemon.deevolution.id,
                "img_url": f'{HttpRequest.build_absolute_uri(request, f"/media/{requested_pokemon.deevolution.image}")}'
            }
        })

    folium_map = folium.Map(location=MOSCOW_CENTER, zoom_start=12)
    for pokemon_entity in PokemonEntity.objects.filter(pokemon=requested_pokemon):
        add_pokemon(
            folium_map,
            pokemon_entity.latitude,
            pokemon_entity.longitude,
            f'{HttpRequest.build_absolute_uri(request, f"/media/{requested_pokemon.image}")}'
        )

    return render(request, 'pokemon.html', context={
        'map': folium_map._repr_html_(), 'pokemon': pokemon
    })
