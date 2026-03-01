from parser import fetch_other_site_products, get_prohockey_categories, fetch_main_site_products, product_exists_on_main
from __init__ import default_client

client = default_client
client.verbose = False

cats = get_prohockey_categories(client)
print('categories count', len(cats))
if cats:
    print('first 5', cats[:5])
cat = cats[0] if cats else None
if cat:
    main = fetch_main_site_products(client, [cat])
    print('main count', len(main))

    others = fetch_other_site_products(client, 'hockeyshans.com.ua/category/2', category=cat)
    print('others count explicit with category', len(others))
    print('sample others 3', others[:3])

    others2 = fetch_other_site_products(client, 'hockeyshans.com.ua', category=cat)
    print('others2 count auto with category', len(others2))
    print('sample others2 3', others2[:3])

    # run again without category filter
    others_nc = fetch_other_site_products(client, 'hockeyshans.com.ua/category/2', category=None)
    print('others count explicit no-category', len(others_nc))
    print('sample others_nc', others_nc[:3])

    others2_nc = fetch_other_site_products(client, 'hockeyshans.com.ua', category=None)
    print('others2 count auto no-category', len(others2_nc))
    print('sample others2_nc', others2_nc[:3])

    missing = [p for p in others2_nc if not product_exists_on_main(p['name'])]
    print('missing no-category', len(missing))
    print('sample missing', missing[:3])
else:
    print('no categories found')
