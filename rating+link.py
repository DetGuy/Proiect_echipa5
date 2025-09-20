from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# initializeaza Chrome
driver = webdriver.Chrome()

hotel_url = "https://www.booking.com/hotel/it/grandhotelflorence.html?aid=356980&label=gog235jc-10CAsocUISZ3JhbmRob3RlbGZsb3JlbmNlSDNYA2jAAYgBAZgBM7gBF8gBDNgBA-gBAfgBAYgCAagCAbgC5KuCxgbAAgHSAiQxMGNiZTFlMC02MWQ2LTRhNWMtODVkYi0xYjA0NTQyOThlYWHYAgHgAgE&sid=fdd43045831c2f048c445c4b1117986e&all_sr_blocks=8124629_246421373_0_2_0&checkin=2025-11-11&checkout=2025-11-12&dest_id=-117543&dest_type=city&dist=0&group_adults=2&group_children=0&hapos=1&highlighted_blocks=8124629_246421373_0_2_0&hpos=1&matching_block_id=8124629_246421373_0_2_0&no_rooms=1&req_adults=2&req_children=0&room1=A%2CA&sb_price_type=total&sr_order=popularity&sr_pri_blocks=8124629_246421373_0_2_0__103600&srepoch=1757507656&srpvid=00c55860e23e0c99&type=total&ucfs=1&"  # pune aici link-ul real
driver.get(hotel_url)

time.sleep(3)  # așteaptă să se încarce pagina complet

try:
    rating = driver.find_element(By.CSS_SELECTOR, "div.b5cd09854e.d10a6220b4").text
    print(f"⭐ Rating: {rating}")
except:
    print("Nu am gasit rating-ul.")

try:
    map_element = driver.find_element(By.CSS_SELECTOR, "a.bui-link")
    map_link = map_element.get_attribute("href")
    print(f"🌍 Coordonate (link harta): {map_link}")
except:
    print("Nu am gasit link-ul catre harta.")

driver.quit()
