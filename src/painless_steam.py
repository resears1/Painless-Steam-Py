from bs4 import BeautifulSoup
import datetime as dt
import requests
import tkinter
from tkinter import*


"""
Program: Painless Steam Listings (painless_steam.py)
Author: Ricky E Sears
Last date modified: 05/07/2020

This program is a web scraper for Valve's Steam website/ web application. 
The scraper gathers as many top-selling listings from the selected category as it can, and outputs it into a text file for the user to read.
This is also a Final Project for my Python class, so it includes some things for the sake of knowledge demonstration, and is not representative
of how small this program *could* be.
"""

# This class was mostly just added for arbitrary purposes
# but it is mildly useful this way, and gives me something to Test
class Urls:
    def __init__(self):
        self._adventure = "Adventure https://store.steampowered.com/search/?tags=21&os=win&filter=topsellers"
        self._action = "Action https://store.steampowered.com/search/?tags=19&os=win&filter=topsellers"
        self._rpg = "RPG https://store.steampowered.com/search/?tags=122&os=win&filter=topsellers"

    def get_action(self):
        return self._action

    def get_adventure(self):
        return self._adventure

    def get_rpg(self):
        return self._rpg


my_urls = Urls()


# - Function that uses a switch statement to return the category name + url
def select_category(selection):
    def adventure_url():
        return my_urls.get_adventure()

    def action_url():
        return my_urls.get_action()

    def rpg_url():
        return my_urls.get_rpg()

    switch_url = {
        1: adventure_url(),
        2: action_url(),
        3: rpg_url()
    }

    # We split the name and the url and put them into unique variables
    url = switch_url.get(selection)
    url = url.split()
    cat_text = url[0]
    url_link = url[1]
    return output_games(url_link, cat_text)


# - This is the actual scraper
def output_games(url, category):
    src = requests.get(url).text
    soup = BeautifulSoup(src, "html.parser")
    listings = {}
    for item in soup.select(".search_result_row.ds_collapse_flag"):
        games = item.select_one(".col.search_price.responsive_secondrow").text
        games = games.strip()
        games = games.split()
        title_check = ""
        for g in games:
            if g != "":
                title = item.select_one(".title").text
                # I was getting repeats, so now we compare the previous title to the next one
                if title_check != title:
                    # This is for those titles that are "discounted", as it's price is actually two prices smashed together
                    # Because it's supposed to strike the first price out during the display, but we don't have that here
                    if item.select_one(".col.search_price.discounted.responsive_secondrow") is not None:
                        prices = item.select_one(".col.search_price.discounted.responsive_secondrow").text
                        prices = prices.strip()
                        prices = prices.split('$')
                        old_price = prices[1]
                        new_price = prices[2]
                        pricing_info = ": $" + new_price + " - DISCOUNTED FROM $" + old_price
                        new_listing = {title: pricing_info}
                        listings.update(new_listing)
                    # Default non-sale prices
                    else:
                        pricing_info = ": " + g
                        new_listing = {title: pricing_info}
                        listings.update(new_listing)
                title_check = title
    # Call write to file and pass the category name + listings
    write_to_file(category, **listings)


# - Writes all of the listings into the file with the current date
def write_to_file(category, **kwargs):
    f = open("steam_listing_output.txt", 'a')
    f.write(category + " (Updated: " + str(dt.datetime.today().strftime("%d-%m-%Y")) + " at " + dt.datetime.now().strftime("%I:%M:%p) \n"))
    f.write("------------------------- \n")
    for key, value in kwargs.items():
        f.write("%s %s \n" % (key, value))
    f.write(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n")
    f.write("\n")
    out_label.config(text=str(category + " listings output to steam_listing_output.txt!"))
    f.close()


# - Called by the "Clear" button - deletes all of the text.
def clear_file():
    f = open("steam_listing_output.txt", 'w')
    f.write("")
    out_label.config(text="steam_listing_output.text has been cleared!")
    f.close()


# - This is the GUI
m = tkinter.Tk();
m.title('Painless Steam Lists')

desc_label = Label(m, text="Painless Steam Lists")
desc_label.grid(row=1, padx=(100,0), pady=5)

label = Label(m, text="Pick a category to output current listings: ")
label.grid(row=2, padx=(100,0), pady=(0, 10))

button1 = tkinter.Button(m, text="Adventure", width=10, command=lambda: select_category(1))
button1.grid(row=3, padx=(100,0))

button2 = tkinter.Button(m, text="Action", width=10, command=lambda: select_category(2))
button2.grid(row=4, padx=(100,0))

button3 = tkinter.Button(m, text="RPG", width=10, command=lambda: select_category(3))
button3.grid(row=5, padx=(100,0))

out_label = Label(m, text="")
out_label.grid(row=6, pady=10)
out_label.place(x=85, y=142)

clear_button = tkinter.Button(m, text="Clear", width=10, command=lambda: clear_file())
clear_button.grid(row=7, padx=(100,0), pady=(25, 5))

exit_button = tkinter.Button(m, text="Exit", width=10, command=m.destroy)
exit_button.grid(row="8", column="1", padx=(0, 10), pady=(15, 5))

m.mainloop()
