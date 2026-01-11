# Steel Darts Optikai Találatazonosító Rendszer

Ez a projekt egy saját fejlesztésű, gépi látáson alapuló automatikus pontszámláló és elemző rendszer steel darts játékhoz. A megoldás három ipari kamera segítségével, valós időben határozza meg a nyilak pontos pozícióját, kiváltva ezzel a manuális adminisztrációt és lehetővé téve a mélyreható statisztikai elemzést.

## Áttekintés

A rendszer célja, hogy költséghatékony alternatívát nyújtson a piacon lévő zárt, drága rendszerekkel (pl. Scolia) szemben. A szoftver nemcsak a pontszámot rögzíti, hanem a nyilak pontos $(x, y)$ koordinátáit is tárolja, így lehetőség nyílik szórásvizsgálatra, hőtérképek (heatmap) generálására és egyéni edzéstervek követésére. A megoldás nyílt architektúrájú, moduláris felépítésű, elválasztva a fizikai érzékelést az üzleti logikától.

## Funkciók

A projekt főbb képességei:

* **Valós idejű detektálás:** A dobás pillanatában azonnali ( < 1 mp) visszajelzés és pontszámítás.
* **Precíz pozíciómeghatározás:** Síkbeli háromszögelés (trianguláció) alkalmazása 3 kamera képéből, hibaszűrő algoritmusokkal.
* **Statisztikai elemzés:** Nemcsak a pontokat, hanem a találatok pontos koordinátáit is menti, lehetővé téve a szórásvizsgálatot.
* **Edzésterv támogatás:** Speciális módok, ahol a cél nem feltétlenül a legmagasabb pontszám, hanem egy adott terület pontos eltalálása.
* **Zajszűrés és stabilitás:** Fejlett "debouncing" algoritmus a fényviszonyok változása és a mozgási elmosódás kiszűrésére.
* **Modern Webes Felület:** Reszponzív, SvelteKit alapú UI, amely bármilyen eszközön (tablet, mobil, PC) megjeleníthető.

## Rendszerarchitektúra

A rendszer három fő rétegre tagolódik:

1.  **Érzékelő réteg (Python & OpenCV):** Felelős a képfeldolgozásért, éldetektálásért és a nyers koordináták kiszámításáért.
2.  **Kommunikációs réteg (Django):** REST API interfészt biztosít a komponensek között.
3.  **Alkalmazás réteg (SvelteKit & SQLite):** Kezeli a játéklogikát, a felhasználói felületet és az adattárolást.

## Előfeltételek

A szoftver futtatásához az alábbiak szükségesek:

* **Python 3.8+**
* **Node.js 16+**
* **OpenCV**
* **SQLite**
* ***3 db csatlakoztatott kamera (a teljes működéshez)***
