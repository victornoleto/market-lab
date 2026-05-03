/plan Eu quero construir um sistema (em python) para fazer o webscrap de systems do myfxbook. O seu objetivo é: fazer o download da lista de systems. Depois, para cada system: 1) fazer o download do "info" e 2) fazer o download do trade history.

Abaixo segue instruções das requisições/cURL e dos payloads esperados.

## Download dos systems

```bash
curl 'https://www.myfxbook.com/paging.html?pt=90&p=1&ts=52&name=HappyForex&_csrf=f5f71a78-06ab-45a9-956d-1a7d7cb537a7&z=0.18475419374203883' \
  -H 'accept: */*' \
  -H 'accept-language: pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -b 'XSRF-TOKEN=f5f71a78-06ab-45a9-956d-1a7d7cb537a7; locale=""; __cflb=0H28vntxK6zZ3c5x6SJLGvCwZC6tfi8nss9mbPR8Vrc; _ga=GA1.1.1428694322.1777605932; timezone=-3.0; dst=0; toolbarWindow=4; _fbp=fb.1.1777605932799.438794536653988950; blockWebNotificationsModalShortTerm=7; pqa=pqa; themeMode=dark; g_state={"i_l":0,"i_ll":1777669919333,"i_b":"Y7llieFV+Pfsug+nwW9SiAsUjeS62xyfvXqUzqaYBKU","i_e":{"enable_itp_optimization":22},"i_et":1777605947661}; sts=1777671606.35.101518.471405|32350e28aa5b99ae6a2e8ef78579ee7d; _ga_XJ8C5872K0=GS2.1.s1777669810$o3$g1$t1777671702$j60$l0$h0; __eoi=ID=0737cdeb83cd0d35:T=1777605931:RT=1777671702:S=AA-AfjZ3MzOu3olSN9RhRyoHtuDu; lastVisitDate=1; _ga_LE2ZJBYJFE=GS2.1.s1777669692$o3$g1$t1777671813$j50$l0$h0' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://www.myfxbook.com/' \
  -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
  -H 'x-requested-with: XMLHttpRequest'
```

Resultado esperado: HTML

```html
<section aria-labelledby="systems-heading" class="portlet-flex ">
  <header class="portlet-title">
    <h2 id="systems-heading" class="portlet-title-text ">
      <span>Systems by HappyForex</span>
    </h2>
  </header>
  <div id="userPageSystemsGrid" class="">
    <div class="title-row padding-10 mobile-hidden  has-actions">
      <div class="title-cell">Name</div>

      <div class="title-cell">Gain</div>
      <div class="title-cell">Drawdown</div>
      <div class="title-cell">Performance</div>
      <div class="title-cell"></div>
    </div>
    <div class="content-row has-actions">
      <div class="grid-table-cell display-flex flex-column gap-5">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-martigrid-v191-real/612872"
          class="bold break-word width-100-percentage"
        >
          OLD Happy MartiGrid v1.9.1 - REAL
        </a>
        <div class="display-flex gap-5 width-max-content">
          <div class="system-info-mini-boxes  real">Real</div>
          <div class="system-info-mini-boxes ">1:500</div>
          <div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div>
        </div>
      </div>
      <div class="grid-table-cell">
        <span class="green">+237.18%</span>
      </div>
      <div class="grid-table-cell">22.31%</div>
      <div class="grid-table-cell">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-martigrid-v191-real/612872"
          target="_blank"
          ><img
            loading="lazy"
            src="https://widgets.myfxbook.com/system-spark.png?id=612872"
            alt="OLD Happy MartiGrid v1.9.1 - REAL performance"
            class="invert-dark-mode"
        /></a>
      </div>
      <div class="grid-table-cell">
        <div class="display-flex justify-content-flex-end" style="gap: 1px">
          <button
            class="btn account-subscribe-button"
            data-toggle="modal"
            data-target="#loginModal"
            data-regFrom="systems"
          >
            Subscribe
          </button>
          <div class="dropdown system-actions-dropdown" data-sid="612872">
            <button
              id="dropdown-toggle-612872"
              class="btn account-action-button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <i class="fas fa-chevron-down"></i>
            </button>

            <ul
              class="dropdown-menu pull-right"
              aria-labelledby="dLabel"
              id="dropdown-menu-612872"
              data-sid="612872"
            >
              <li id="copy-sys-612872" aria-haspopup="true">
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Copy
                </div>
              </li>

              <li>
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Add to watch
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="content-row has-actions">
      <div class="grid-table-cell display-flex flex-column gap-5">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-forex-v241-real/1152318"
          class="bold break-word width-100-percentage"
        >
          OLD Happy Forex v2.4.1 - REAL (FortFS- set 3)
        </a>
        <div class="display-flex gap-5 width-max-content">
          <div class="system-info-mini-boxes  real">Real</div>
          <div class="system-info-mini-boxes ">1:500</div>
          <div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div>
        </div>
      </div>
      <div class="grid-table-cell">
        <span class="green">+154.03%</span>
      </div>
      <div class="grid-table-cell">23.70%</div>
      <div class="grid-table-cell">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-forex-v241-real/1152318"
          target="_blank"
          ><img
            loading="lazy"
            src="https://widgets.myfxbook.com/system-spark.png?id=1152318"
            alt="OLD Happy Forex v2.4.1 - REAL (FortFS- set 3) performance"
            class="invert-dark-mode"
        /></a>
      </div>
      <div class="grid-table-cell">
        <div class="display-flex justify-content-flex-end" style="gap: 1px">
          <button
            class="btn account-subscribe-button"
            data-toggle="modal"
            data-target="#loginModal"
            data-regFrom="systems"
          >
            Subscribe
          </button>
          <div class="dropdown system-actions-dropdown" data-sid="1152318">
            <button
              id="dropdown-toggle-1152318"
              class="btn account-action-button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <i class="fas fa-chevron-down"></i>
            </button>

            <ul
              class="dropdown-menu pull-right"
              aria-labelledby="dLabel"
              id="dropdown-menu-1152318"
              data-sid="1152318"
            >
              <li id="copy-sys-1152318" aria-haspopup="true">
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Copy
                </div>
              </li>

              <li>
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Add to watch
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="content-row has-actions">
      <div class="grid-table-cell display-flex flex-column gap-5">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-market-hours-v231/1407880"
          class="bold break-word width-100-percentage"
        >
          OLD Happy Market Hours v2.3.1
        </a>
        <div class="display-flex gap-5 width-max-content">
          <div class="system-info-mini-boxes demo ">Demo</div>
          <div class="system-info-mini-boxes ">1:500</div>
          <div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div>
        </div>
      </div>
      <div class="grid-table-cell">
        <span class="green">+4,550.23%</span>
      </div>
      <div class="grid-table-cell">10.16%</div>
      <div class="grid-table-cell">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-market-hours-v231/1407880"
          target="_blank"
          ><img
            loading="lazy"
            src="https://widgets.myfxbook.com/system-spark.png?id=1407880"
            alt="OLD Happy Market Hours v2.3.1 performance"
            class="invert-dark-mode"
        /></a>
      </div>
      <div class="grid-table-cell">
        <div class="display-flex justify-content-flex-end" style="gap: 1px">
          <button
            class="btn account-subscribe-button"
            data-toggle="modal"
            data-target="#loginModal"
            data-regFrom="systems"
          >
            Subscribe
          </button>
          <div class="dropdown system-actions-dropdown" data-sid="1407880">
            <button
              id="dropdown-toggle-1407880"
              class="btn account-action-button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <i class="fas fa-chevron-down"></i>
            </button>

            <ul
              class="dropdown-menu pull-right"
              aria-labelledby="dLabel"
              id="dropdown-menu-1407880"
              data-sid="1407880"
            >
              <li>
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Add to watch
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="content-row has-actions">
      <div class="grid-table-cell display-flex flex-column gap-5">
        <a
          href="https://www.myfxbook.com/members/HappyForex/happy-breakout-v10-closed-au/1603276"
          class="bold break-word width-100-percentage"
        >
          Happy Breakout v1.0 - (Closed AU account)
        </a>
        <div class="display-flex gap-5 width-max-content">
          <div class="system-info-mini-boxes  real">Real</div>
          <div class="system-info-mini-boxes ">1:500</div>
          <div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div>
        </div>
      </div>
      <div class="grid-table-cell">
        <span class="green">+77.32%</span>
      </div>
      <div class="grid-table-cell">29.71%</div>
      <div class="grid-table-cell">
        <a
          href="https://www.myfxbook.com/members/HappyForex/happy-breakout-v10-closed-au/1603276"
          target="_blank"
          ><img
            loading="lazy"
            src="https://widgets.myfxbook.com/system-spark.png?id=1603276"
            alt="Happy Breakout v1.0 - (Closed AU account) performance"
            class="invert-dark-mode"
        /></a>
      </div>
      <div class="grid-table-cell">
        <div class="display-flex justify-content-flex-end" style="gap: 1px">
          <button
            class="btn account-subscribe-button"
            data-toggle="modal"
            data-target="#loginModal"
            data-regFrom="systems"
          >
            Subscribe
          </button>
          <div class="dropdown system-actions-dropdown" data-sid="1603276">
            <button
              id="dropdown-toggle-1603276"
              class="btn account-action-button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <i class="fas fa-chevron-down"></i>
            </button>

            <ul
              class="dropdown-menu pull-right"
              aria-labelledby="dLabel"
              id="dropdown-menu-1603276"
              data-sid="1603276"
            >
              <li id="copy-sys-1603276" aria-haspopup="true">
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Copy
                </div>
              </li>

              <li>
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Add to watch
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="content-row has-actions">
      <div class="grid-table-cell display-flex flex-column gap-5">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-news-v141/1612420"
          class="bold break-word width-100-percentage"
        >
          OLD Happy News v1.4.1
        </a>
        <div class="display-flex gap-5 width-max-content">
          <div class="system-info-mini-boxes demo ">Demo</div>
          <div class="system-info-mini-boxes ">1:500</div>
          <div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div>
        </div>
      </div>
      <div class="grid-table-cell">
        <span class="green">+447.06%</span>
      </div>
      <div class="grid-table-cell">39.26%</div>
      <div class="grid-table-cell">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-news-v141/1612420"
          target="_blank"
          ><img
            loading="lazy"
            src="https://widgets.myfxbook.com/system-spark.png?id=1612420"
            alt="OLD Happy News v1.4.1 performance"
            class="invert-dark-mode"
        /></a>
      </div>
      <div class="grid-table-cell">
        <div class="display-flex justify-content-flex-end" style="gap: 1px">
          <button
            class="btn account-subscribe-button"
            data-toggle="modal"
            data-target="#loginModal"
            data-regFrom="systems"
          >
            Subscribe
          </button>
          <div class="dropdown system-actions-dropdown" data-sid="1612420">
            <button
              id="dropdown-toggle-1612420"
              class="btn account-action-button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <i class="fas fa-chevron-down"></i>
            </button>

            <ul
              class="dropdown-menu pull-right"
              aria-labelledby="dLabel"
              id="dropdown-menu-1612420"
              data-sid="1612420"
            >
              <li>
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Add to watch
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="content-row has-actions">
      <div class="grid-table-cell display-flex flex-column gap-5">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-way-v12-real/2123808"
          class="bold break-word width-100-percentage"
        >
          OLD Happy Way v1.2 - REAL
        </a>
        <div class="display-flex gap-5 width-max-content">
          <div class="system-info-mini-boxes  real">Real</div>
          <div class="system-info-mini-boxes ">1:500</div>
          <div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div>
        </div>
      </div>
      <div class="grid-table-cell">
        <span class="green">+44.79%</span>
      </div>
      <div class="grid-table-cell">32.31%</div>
      <div class="grid-table-cell">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-way-v12-real/2123808"
          target="_blank"
          ><img
            loading="lazy"
            src="https://widgets.myfxbook.com/system-spark.png?id=2123808"
            alt="OLD Happy Way v1.2 - REAL performance"
            class="invert-dark-mode"
        /></a>
      </div>
      <div class="grid-table-cell">
        <div class="display-flex justify-content-flex-end" style="gap: 1px">
          <button
            class="btn account-subscribe-button"
            data-toggle="modal"
            data-target="#loginModal"
            data-regFrom="systems"
          >
            Subscribe
          </button>
          <div class="dropdown system-actions-dropdown" data-sid="2123808">
            <button
              id="dropdown-toggle-2123808"
              class="btn account-action-button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <i class="fas fa-chevron-down"></i>
            </button>

            <ul
              class="dropdown-menu pull-right"
              aria-labelledby="dLabel"
              id="dropdown-menu-2123808"
              data-sid="2123808"
            >
              <li id="copy-sys-2123808" aria-haspopup="true">
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Copy
                </div>
              </li>

              <li>
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Add to watch
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="content-row has-actions">
      <div class="grid-table-cell display-flex flex-column gap-5">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-algorithm-pro-v14/2373850"
          class="bold break-word width-100-percentage"
        >
          OLD Happy Algorithm PRO v1.4 - REAL (SET1)
        </a>
        <div class="display-flex gap-5 width-max-content">
          <div class="system-info-mini-boxes  real">Real</div>
          <div class="system-info-mini-boxes ">1:500</div>
          <div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div>
        </div>
      </div>
      <div class="grid-table-cell">
        <span class="green">+56.83%</span>
      </div>
      <div class="grid-table-cell">39.53%</div>
      <div class="grid-table-cell">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-algorithm-pro-v14/2373850"
          target="_blank"
          ><img
            loading="lazy"
            src="https://widgets.myfxbook.com/system-spark.png?id=2373850"
            alt="OLD Happy Algorithm PRO v1.4 - REAL (SET1) performance"
            class="invert-dark-mode"
        /></a>
      </div>
      <div class="grid-table-cell">
        <div class="display-flex justify-content-flex-end" style="gap: 1px">
          <button
            class="btn account-subscribe-button"
            data-toggle="modal"
            data-target="#loginModal"
            data-regFrom="systems"
          >
            Subscribe
          </button>
          <div class="dropdown system-actions-dropdown" data-sid="2373850">
            <button
              id="dropdown-toggle-2373850"
              class="btn account-action-button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <i class="fas fa-chevron-down"></i>
            </button>

            <ul
              class="dropdown-menu pull-right"
              aria-labelledby="dLabel"
              id="dropdown-menu-2373850"
              data-sid="2373850"
            >
              <li id="copy-sys-2373850" aria-haspopup="true">
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Copy
                </div>
              </li>

              <li>
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Add to watch
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="content-row has-actions">
      <div class="grid-table-cell display-flex flex-column gap-5">
        <a
          href="https://www.myfxbook.com/members/HappyForex/happy-gold-icmarkets-m30/2421356"
          class="bold break-word width-100-percentage"
        >
          Happy Gold - ICMarkets (M30)
        </a>
        <div class="display-flex gap-5 width-max-content">
          <div class="system-info-mini-boxes demo ">Demo</div>
          <div class="system-info-mini-boxes ">1:500</div>
          <div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div>
        </div>
      </div>
      <div class="grid-table-cell">
        <span class="green">+220,189.74%</span>
      </div>
      <div class="grid-table-cell">22.61%</div>
      <div class="grid-table-cell">
        <a
          href="https://www.myfxbook.com/members/HappyForex/happy-gold-icmarkets-m30/2421356"
          target="_blank"
          ><img
            loading="lazy"
            src="https://widgets.myfxbook.com/system-spark.png?id=2421356"
            alt="Happy Gold - ICMarkets (M30) performance"
            class="invert-dark-mode"
        /></a>
      </div>
      <div class="grid-table-cell">
        <div class="display-flex justify-content-flex-end" style="gap: 1px">
          <button
            class="btn account-subscribe-button"
            data-toggle="modal"
            data-target="#loginModal"
            data-regFrom="systems"
          >
            Subscribe
          </button>
          <div class="dropdown system-actions-dropdown" data-sid="2421356">
            <button
              id="dropdown-toggle-2421356"
              class="btn account-action-button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <i class="fas fa-chevron-down"></i>
            </button>

            <ul
              class="dropdown-menu pull-right"
              aria-labelledby="dLabel"
              id="dropdown-menu-2421356"
              data-sid="2421356"
            >
              <li>
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Add to watch
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="content-row has-actions">
      <div class="grid-table-cell display-flex flex-column gap-5">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-martigrid-v191-multipairs/2483126"
          class="bold break-word width-100-percentage"
        >
          OLD Happy MartiGrid v1.9.1 (Multipairs)- REAL
        </a>
        <div class="display-flex gap-5 width-max-content">
          <div class="system-info-mini-boxes  real">Real</div>
          <div class="system-info-mini-boxes ">1:500</div>
          <div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div>
        </div>
      </div>
      <div class="grid-table-cell">
        <span class="green">+192.46%</span>
      </div>
      <div class="grid-table-cell">62.97%</div>
      <div class="grid-table-cell">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-martigrid-v191-multipairs/2483126"
          target="_blank"
          ><img
            loading="lazy"
            src="https://widgets.myfxbook.com/system-spark.png?id=2483126"
            alt="OLD Happy MartiGrid v1.9.1 (Multipairs)- REAL performance"
            class="invert-dark-mode"
        /></a>
      </div>
      <div class="grid-table-cell">
        <div class="display-flex justify-content-flex-end" style="gap: 1px">
          <button
            class="btn account-subscribe-button"
            data-toggle="modal"
            data-target="#loginModal"
            data-regFrom="systems"
          >
            Subscribe
          </button>
          <div class="dropdown system-actions-dropdown" data-sid="2483126">
            <button
              id="dropdown-toggle-2483126"
              class="btn account-action-button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <i class="fas fa-chevron-down"></i>
            </button>

            <ul
              class="dropdown-menu pull-right"
              aria-labelledby="dLabel"
              id="dropdown-menu-2483126"
              data-sid="2483126"
            >
              <li id="copy-sys-2483126" aria-haspopup="true">
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Copy
                </div>
              </li>

              <li>
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Add to watch
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
    <div class="content-row has-actions">
      <div class="grid-table-cell display-flex flex-column gap-5">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-frequency-v11-real/3568877"
          class="bold break-word width-100-percentage"
        >
          OLD Happy Frequency v1.1 - REAL (9 pairs)
        </a>
        <div class="display-flex gap-5 width-max-content">
          <div class="system-info-mini-boxes  real">Real</div>
          <div class="system-info-mini-boxes ">1:500</div>
          <div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div>
        </div>
      </div>
      <div class="grid-table-cell">
        <span class="green">+1,281.52%</span>
      </div>
      <div class="grid-table-cell">73.97%</div>
      <div class="grid-table-cell">
        <a
          href="https://www.myfxbook.com/members/HappyForex/old-happy-frequency-v11-real/3568877"
          target="_blank"
          ><img
            loading="lazy"
            src="https://widgets.myfxbook.com/system-spark.png?id=3568877"
            alt="OLD Happy Frequency v1.1 - REAL (9 pairs) performance"
            class="invert-dark-mode"
        /></a>
      </div>
      <div class="grid-table-cell">
        <div class="display-flex justify-content-flex-end" style="gap: 1px">
          <button
            class="btn account-subscribe-button"
            data-toggle="modal"
            data-target="#loginModal"
            data-regFrom="systems"
          >
            Subscribe
          </button>
          <div class="dropdown system-actions-dropdown" data-sid="3568877">
            <button
              id="dropdown-toggle-3568877"
              class="btn account-action-button"
              aria-haspopup="true"
              aria-expanded="false"
            >
              <i class="fas fa-chevron-down"></i>
            </button>

            <ul
              class="dropdown-menu pull-right"
              aria-labelledby="dLabel"
              id="dropdown-menu-3568877"
              data-sid="3568877"
            >
              <li id="copy-sys-3568877" aria-haspopup="true">
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Copy
                </div>
              </li>

              <li>
                <div
                  data-toggle="modal"
                  data-target="#loginModal"
                  data-regFrom="systems"
                >
                  Add to watch
                </div>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div class="paging-container">
      <ul
        class="pagination responsive-paging"
        container="user-systems"
        history="false"
        reloadAds="false"
        scrollToTop="false"
      >
        <li class="prev">
          <a
            href="javascript:void(0);"
            class="btn disabled-a"
            onclick="return false;"
            title="Prev"
          >
            <i class="fas fa-angle-left"></i>
          </a>
        </li>
        <li class="active">
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=1&ts=52&name=HappyForex"
            page="1"
          >
            1
          </a>
        </li>
        <li>
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=2&ts=52&name=HappyForex"
            page="2"
          >
            2
          </a>
        </li>
        <li>
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=3&ts=52&name=HappyForex"
            page="3"
          >
            3
          </a>
        </li>
        <li>
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=4&ts=52&name=HappyForex"
            page="4"
          >
            4
          </a>
        </li>
        <li>
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=5&ts=52&name=HappyForex"
            page="5"
          >
            5
          </a>
        </li>
        <li>
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=6&ts=52&name=HappyForex"
            page="6"
            lastPage="true"
          >
            6
          </a>
        </li>
        <li class="next">
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=2&ts=52&name=HappyForex"
            page="2"
            title="Next"
          >
            <i class="fas fa-angle-right"></i>
          </a>
        </li>
      </ul>

      <ul
        class="pagination responsive-paging mobile-paging"
        container="user-systems"
        history="false"
        reloadAds="false"
        scrollToTop="false"
        style="display: none;"
      >
        <li class="prev">
          <a
            href="javascript:void(0);"
            class="btn disabled-a"
            onclick="return false;"
            title="Prev"
          >
            <i class="fas fa-angle-left"></i>
          </a>
        </li>
        <li class="active">
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=1&ts=52&name=HappyForex"
            page="1"
          >
            1
          </a>
        </li>
        <li>
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=2&ts=52&name=HappyForex"
            page="2"
          >
            2
          </a>
        </li>
        <li>
          <a class="btn disabled-a bold">..</a>
        </li>
        <li>
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=5&ts=52&name=HappyForex"
            page="5"
          >
            5
          </a>
        </li>
        <li>
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=6&ts=52&name=HappyForex"
            page="6"
            lastPage="true"
          >
            6
          </a>
        </li>
        <li class="next">
          <a
            href="javascript:void(0);"
            class="btn paging-btn"
            params="?pt=90&p=2&ts=52&name=HappyForex"
            page="2"
            title="Next"
          >
            <i class="fas fa-angle-right"></i>
          </a>
        </li>
      </ul>
    </div>
  </div>
</section>
```

O que importa para a gente nesse html é o seguinte:

```html
<div class="content-row has-actions">
  <div class="grid-table-cell display-flex flex-column gap-5">
    <a
      href="https://www.myfxbook.com/members/HappyForex/old-happy-forex-v241-real/1152318"
      class="bold break-word width-100-percentage"
    >
      OLD Happy Forex v2.4.1 - REAL (FortFS- set 3)
    </a>
    <div class="display-flex gap-5 width-max-content">
      <div class="system-info-mini-boxes  real">Real</div>
      <div class="system-info-mini-boxes ">1:500</div>
      <div class="system-info-mini-boxes mobile-hidden">MetaTrader 4</div>
    </div>
  </div>
  <div class="grid-table-cell">
    <span class="green">+154.03%</span>
  </div>
  <div class="grid-table-cell">23.70%</div>
  <div class="grid-table-cell">
    <a
      href="https://www.myfxbook.com/members/HappyForex/old-happy-forex-v241-real/1152318"
      target="_blank"
      ><img
        loading="lazy"
        src="https://widgets.myfxbook.com/system-spark.png?id=1152318"
        alt="OLD Happy Forex v2.4.1 - REAL (FortFS- set 3) performance"
        class="invert-dark-mode"
    /></a>
  </div>
  <div class="grid-table-cell">
    <div class="display-flex justify-content-flex-end" style="gap: 1px">
      <button
        class="btn account-subscribe-button"
        data-toggle="modal"
        data-target="#loginModal"
        data-regfrom="systems"
      >
        Subscribe
      </button>
      <div class="dropdown system-actions-dropdown" data-sid="1152318">
        <button
          id="dropdown-toggle-1152318"
          class="btn account-action-button"
          aria-haspopup="true"
          aria-expanded="false"
        >
          <i class="fas fa-chevron-down"></i>
        </button>

        <ul
          class="dropdown-menu pull-right"
          aria-labelledby="dLabel"
          id="dropdown-menu-1152318"
          data-sid="1152318"
        >
          <li id="copy-sys-1152318" aria-haspopup="true">
            <div
              data-toggle="modal"
              data-target="#loginModal"
              data-regfrom="systems"
            >
              Copy
            </div>
          </li>

          <li>
            <div
              data-toggle="modal"
              data-target="#loginModal"
              data-regfrom="systems"
            >
              Add to watch
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</div>
```

Observe o seguinte elemento:

```html
<a
  href="https://www.myfxbook.com/members/HappyForex/old-happy-forex-v241-real/1152318"
  class="bold break-word width-100-percentage"
>
  OLD Happy Forex v2.4.1 - REAL (FortFS- set 3)
</a>
```

Aqui temos: 1) nome da estratégia e o mais importante 2) a url. O que importa para gente é o que vamos chamar de accountOid, que é o numero no final da url: **1152318**

Se fizermos o cURL para a página do system:

```bash
curl 'https://www.myfxbook.com/members/HappyForex/old-happy-forex-v241-real/1152318' \
  -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
  -H 'accept-language: pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -b 'XSRF-TOKEN=f5f71a78-06ab-45a9-956d-1a7d7cb537a7; locale=""; __cflb=0H28vntxK6zZ3c5x6SJLGvCwZC6tfi8nss9mbPR8Vrc; _ga=GA1.1.1428694322.1777605932; timezone=-3.0; dst=0; toolbarWindow=4; _fbp=fb.1.1777605932799.438794536653988950; blockWebNotificationsModalShortTerm=7; pqa=pqa; themeMode=dark; sts=1777671606.35.101518.471405|32350e28aa5b99ae6a2e8ef78579ee7d; lastVisitDate=1; __eoi=ID=0737cdeb83cd0d35:T=1777605931:RT=1777672016:S=AA-AfjZ3MzOu3olSN9RhRyoHtuDu; _ga_XJ8C5872K0=GS2.1.s1777669810$o3$g1$t1777672033$j49$l0$h0; g_state={"i_l":0,"i_ll":1777672036281,"i_b":"ewRyBrbprmL438CcR8SQZR+t/gTOUfu8SQc3Z04p5IU","i_e":{"enable_itp_optimization":22},"i_et":1777605947661}; _ga_LE2ZJBYJFE=GS2.1.s1777669692$o3$g1$t1777672095$j43$l0$h0' \
  -H 'pragma: no-cache' \
  -H 'priority: u=0, i' \
  -H 'referer: https://www.myfxbook.com/' \
  -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: document' \
  -H 'sec-fetch-mode: navigate' \
  -H 'sec-fetch-site: same-origin' \
  -H 'sec-fetch-user: ?1' \
  -H 'upgrade-insecure-requests: 1' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36'
```

O resultado vai ser um HTML da página inteira, no entanto o que importa para gente é o seguinte elemento:

```html
<div class="tab-pane active" id="infoStats">
  <div class="table-scrollable-borderless">
    <table class="table-hover table-small">
      <tbody>
        <tr>
          <td>
            <label
              class="custom-analysis-popover"
              data-title="Gain"
              data-content="Time-Weighted Return (TWR) that measures the performance of a dollar invested in the system since inception.&lt;br/&gt;TWR measurement is required by the Global Investment Performance Standards published by the CFA Institute. Its distinguishing characteristic is that cash inflows, cash outflows and amounts invested over different time periods have no impact on the return."
              data-original-title=""
              title=""
            >
              <span><b class="dotted">Gain :</b></span>
            </label>
          </td>
          <td>
            <span
              ><b><span class="green">+154.03%</span></b></span
            >
          </td>
        </tr>
        <tr>
          <td>
            <label
              class="custom-analysis-popover"
              data-title="Absolute Gain"
              data-content="Return of the investment as a percentage of the total deposits.&lt;br/&gt;By definition, new deposits will affect the absolute gain."
            >
              <span class="dotted"> Abs. Gain: </span>
            </label>
          </td>
          <td>
            <span><span class="green">+117.81%</span></span>
          </td>
        </tr>
      </tbody>
    </table>
    <hr />
    <table class="table-hover table-small">
      <tbody>
        <tr>
          <td>
            <label
              class="custom-analysis-popover"
              data-title="Daily Gain"
              data-content="Daily compound rate of return leading to the total gain."
              data-original-title=""
              title=""
            >
              <span class="dotted"> Daily </span>
            </label>
          </td>
          <td><span>0.02%</span></td>
        </tr>
        <tr>
          <td>
            <label
              class="custom-analysis-popover"
              data-title="Monthly Gain"
              data-content="Monthly compound rate of return leading to the total gain."
              data-original-title=""
              title=""
            >
              <span class="dotted"> Monthly: </span>
            </label>
          </td>
          <td><span>1.20% </span></td>
        </tr>
        <tr>
          <td>Drawdown:</td>
          <td><span>23.70% </span></td>
        </tr>
      </tbody>
    </table>
    <hr />
    <table class="table-hover table-small">
      <tbody>
        <tr>
          <td>Balance:</td>
          <td>
            <span>
              <span id="statsBalance">$3,415.33</span>
            </span>
          </td>
        </tr>
        <tr>
          <td>Equity:</td>
          <td>
            <span>
              <span class="font11"> (100.00%) </span>
              <span id="statsEquity">$3,415.33</span>
            </span>
          </td>
        </tr>
        <tr>
          <td>Highest:</td>
          <td>
            <span>
              <span class="gray font11"> (Jun 01) </span>
              <span> $3,415.32 </span>
            </span>
          </td>
        </tr>
        <tr>
          <td>Profit:</td>
          <td>
            <span>
              <span class="green">$1,847.33</span>
            </span>
          </td>
        </tr>
        <tr>
          <td>Interest:</td>
          <td>
            <span> $0.00 </span>
          </td>
        </tr>
      </tbody>
    </table>
    <hr />
    <table class="table-hover table-small">
      <tbody>
        <tr>
          <td>Deposits:</td>
          <td>
            <span> $1,568.00 </span>
          </td>
        </tr>
        <tr>
          <td>Withdrawals:</td>
          <td>
            <span> $0.01 </span>
          </td>
        </tr>
      </tbody>
    </table>
    <hr />
    <table class="table-hover table-small">
      <tbody>
        <tr>
          <td>Updated</td>
          <td>
            <span class="floatNone" id="lastUpdatedTime" time="">
              Jun 18, 2021 at 05:52
            </span>
          </td>
        </tr>
        <tr>
          <td>Tracking</td>
          <td><span id="totalTracking">198 </span></td>
        </tr>
      </tbody>
    </table>
  </div>
</div>
```

Com esse elemento podemos extrair as informações mais importantes do system:

- Gain: +154.03%
- Abs. Gain: +117.81%
- Daily 0.02%
- Monthly: 1.20%
- Drawdown: 23.70%
- Balance: $3,415.33
- Equity: (100.00%) $3,415.33
- Highest: (Jun 01) $3,415.32
- Profit: $1,847.33
- Interest: $0.00
- Deposits: $1,568.00
- Withdrawals: $0.01
- Updated: Jun 18, 2021 at 05:52
- Tracking: 198

Outras informações relevantes são extraídas desse elemento:

```html
<div class="portfolio-resolve-account-type">
  <span>
    Real (USD),
    <a
      class="underline"
      href="https://www.myfxbook.com/reviews/brokers/fort-financial-services/814372,1"
      >Fort Financial Services</a
    >
    , Technical , Automated , 1:500 , MetaTrader 4
  </span>
</div>
```

Principalmente:

- Tipo da conta (ex: Real ou Demo);
- Leverage (ex: 1:500)

Com essas informações do system salvas/extraídas podemos ir para o download do trade history. O cURL é simples, mas infelizmente o retorno também é um HTML, então vamos precisar usar algum tipo de parser aqui.

## Download do Trade History

```bash
curl 'https://www.myfxbook.com/paging.html?pt=4&p=1&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05%2000:00&end=2021-06-14%2006:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640&_csrf=f5f71a78-06ab-45a9-956d-1a7d7cb537a7&z=0.7116246877055796' \
  -H 'accept: */*' \
  -H 'accept-language: pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7' \
  -H 'cache-control: no-cache' \
  -b 'XSRF-TOKEN=f5f71a78-06ab-45a9-956d-1a7d7cb537a7; locale=""; __cflb=0H28vntxK6zZ3c5x6SJLGvCwZC6tfi8nss9mbPR8Vrc; _ga=GA1.1.1428694322.1777605932; timezone=-3.0; dst=0; toolbarWindow=4; _fbp=fb.1.1777605932799.438794536653988950; blockWebNotificationsModalShortTerm=7; pqa=pqa; themeMode=dark; __eoi=ID=0737cdeb83cd0d35:T=1777605931:RT=1777672016:S=AA-AfjZ3MzOu3olSN9RhRyoHtuDu; _ga_XJ8C5872K0=GS2.1.s1777669810$o3$g1$t1777672103$j58$l0$h0; g_state={"i_l":0,"i_ll":1777672106237,"i_b":"ewRyBrbprmL438CcR8SQZR+t/gTOUfu8SQc3Z04p5IU","i_e":{"enable_itp_optimization":22},"i_et":1777605947661}; sts=1777672594.776.101517.65471|32350e28aa5b99ae6a2e8ef78579ee7d; _ga_LE2ZJBYJFE=GS2.1.s1777669692$o3$g1$t1777672597$j56$l0$h0' \
  -H 'pragma: no-cache' \
  -H 'priority: u=1, i' \
  -H 'referer: https://www.myfxbook.com/' \
  -H 'sec-ch-ua: "Google Chrome";v="147", "Not.A/Brand";v="8", "Chromium";v="147"' \
  -H 'sec-ch-ua-mobile: ?0' \
  -H 'sec-ch-ua-platform: "Linux"' \
  -H 'sec-fetch-dest: empty' \
  -H 'sec-fetch-mode: cors' \
  -H 'sec-fetch-site: same-origin' \
  -H 'user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36' \
  -H 'x-requested-with: XMLHttpRequest'
```

Retorno:

```html
<input
  id="historyTableSort"
  type="hidden"
  sorttype="4"
  accountOid="1152318"
  loc="x"
  start="2015-01-05 00:00"
  end="2021-06-14 06:00"
  invitation="&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd="
  total="1640"
/>
<div id="history">
  <input
    id="filterHistoryParams"
    type="hidden"
    loc="x"
    accountOid="1152318"
    startDate="2015-01-05 00:00"
    endDate="2021-06-14 06:00"
    pagingSortBy="28"
    pagingSortType="2"
    magicNumbersString=""
    symbols=""
    orderTagList=""
    daysList=""
    hoursList=""
    commentParam=""
    buySellList=""
    yieldStart=""
    yieldEnd=""
    netProfitStart=""
    netProfitEnd=""
    durationStart=""
    durationEnd=""
    takeProfitStart=""
    takeProfitEnd=""
    stopLoss=""
    stopLossEnd=""
    sizingStart=""
    sizingEnd=""
    selectedTime=""
    pipsStart=""
    pipsEnd=""
    invitation=""
  />

  <input type="hidden" id="historySize" value="1640" />
  <div class="table-responsive white-space-nowrap">
    <table
      class="table table-striped text-center table-hover"
      id="tradingHistoryTable"
    >
      <thead id="historyTableHeader">
        <tr>
          <th></th>
          <th sortBy="27" class="openDate" order="1">
            <a>Open Date</a><span class="    "></span>
          </th>
          <th sortBy="28" class="closeDate" order="1">
            <a>Close date</a
            ><span class="                    sorting-desc            "></span>
          </th>
          <th sortBy="29" class="symbol" order="1">
            <a>Symbol</a><span class="    "></span>
          </th>
          <th sortBy="7" class="action" order="1">
            <a>Action</a><span class="    "></span>
          </th>
          <th sortBy="30" class="lots" order="1">
            <a> Lots </a><span class="    "></span>
          </th>
          <th sortBy="34" class="openPrice" order="1">
            <a>Open Price</a><span class="    "></span>
          </th>
          <th sortBy="35" class="closePrice" order="1">
            <a>Close Price</a><span class="    "></span>
          </th>
          <th sortBy="37" class="pips" order="1">
            <a>Pips</a><span class="    "></span>
          </th>
          <th sortBy="59" class="profits" order="1">
            <a>Profit<br />(USD)</a><span class="    "></span>
          </th>
          <th sortBy="57" class="durations" order="1">
            <a>Duration</a><span class="    "></span>
          </th>
          <th sortBy="55" class="change" order="1">
            <a>Gain</a><span class="    "></span>
          </th>
          <th>
            <i
              data-toggle="history-popover"
              data-content="
                            Here you can see the analysis of each trade. The chart shows a normalized progress curve of each trade as it happened (when possible to calculate).
                            <br/>
                            Hover over the chart area to reveal even more trade data.
                            <br/><br/>
                            <div class='text-center'>
                                <b>Verify your account to unlock this feature!</b>
                                <br/>
                                <img style='max-width:90%; min-height: 300px' src='https://static.mfbcdn.net/images/tradeAnalyticsNew.png' alt='Trade Analytics'/>
                            </div>
                            "
              data-title="Trade Analytics"
              class="fa fa-info-circle"
            ></i>
          </th>
          <th></th>
        </tr>
      </thead>

      <tbody>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11558090443"
          data-record="11558090443"
          data-oid="htradingActivity11558090443"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11558090443" params="h11558090443" name="tagWindow">
            <div id="tagWindowh11558090443" class="tagWindowDiv">
              <i id="pointerh11558090443" class="$class"></i>
            </div>
          </td>
          <td class="brokerTime">05.31.2021 03:33</td>
          <td style="display:none" class="userTime">05.30.2021 22:33</td>

          <td class="brokerTime">06.01.2021 02:31</td>
          <td style="display:none" class="userTime">05.31.2021 21:31</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1622431980000"
            closeTime="1622514660000"
            tradeOid="h11558090443"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.77041</td>
          <td>0.77451</td>
          <td>
            <span class="green">41.0</span>
          </td>
          <td class="green">4.10</td>
          <td>22h 58m</td>
          <td>
            <span class="green">0.12%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11558090443"
            data-type="h"
            id="commentPopOverhtradingActivity11558090443"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11558090436"
          data-record="11558090436"
          data-oid="htradingActivity11558090436"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11558090436" params="h11558090436" name="tagWindow">
            <div id="tagWindowh11558090436" class="tagWindowDiv">
              <i id="pointerh11558090436" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.28.2021 08:44</td>
          <td style="display:none" class="userTime">05.28.2021 03:44</td>

          <td class="brokerTime">06.01.2021 02:31</td>
          <td style="display:none" class="userTime">05.31.2021 21:31</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1622191440000"
            closeTime="1622514660000"
            tradeOid="h11558090436"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.77331</td>
          <td>0.77451</td>
          <td>
            <span class="green">12.0</span>
          </td>
          <td class="green">1.20</td>
          <td>3d</td>
          <td>
            <span class="green">0.04%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11558090436"
            data-type="h"
            id="commentPopOverhtradingActivity11558090436"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11558090429"
          data-record="11558090429"
          data-oid="htradingActivity11558090429"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11558090429" params="h11558090429" name="tagWindow">
            <div id="tagWindowh11558090429" class="tagWindowDiv">
              <i id="pointerh11558090429" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.27.2021 03:21</td>
          <td style="display:none" class="userTime">05.26.2021 22:21</td>

          <td class="brokerTime">06.01.2021 02:31</td>
          <td style="display:none" class="userTime">05.31.2021 21:31</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1622085660000"
            closeTime="1622514660000"
            tradeOid="h11558090429"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.77344</td>
          <td>0.77451</td>
          <td>
            <span class="green">10.7</span>
          </td>
          <td class="green">1.07</td>
          <td>4d</td>
          <td>
            <span class="green">0.03%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11558090429"
            data-type="h"
            id="commentPopOverhtradingActivity11558090429"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11558090422"
          data-record="11558090422"
          data-oid="htradingActivity11558090422"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11558090422" params="h11558090422" name="tagWindow">
            <div id="tagWindowh11558090422" class="tagWindowDiv">
              <i id="pointerh11558090422" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.26.2021 18:01</td>
          <td style="display:none" class="userTime">05.26.2021 13:01</td>

          <td class="brokerTime">06.01.2021 02:31</td>
          <td style="display:none" class="userTime">05.31.2021 21:31</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="14"
            openTime="1622052060000"
            closeTime="1622514660000"
            tradeOid="h11558090422"
            location="a"
          >
            <a
              title="EURCHF"
              href="#browserListData"
              class="underline pointer symbolName"
              >EURCHF</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>1.09511</td>
          <td>1.09871</td>
          <td>
            <span class="green">36.0</span>
          </td>
          <td class="green">4.01</td>
          <td>5d</td>
          <td>
            <span class="green">0.12%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11558090422"
            data-type="h"
            id="commentPopOverhtradingActivity11558090422"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11558090415"
          data-record="11558090415"
          data-oid="htradingActivity11558090415"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11558090415" params="h11558090415" name="tagWindow">
            <div id="tagWindowh11558090415" class="tagWindowDiv">
              <i id="pointerh11558090415" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.26.2021 17:57</td>
          <td style="display:none" class="userTime">05.26.2021 12:57</td>

          <td class="brokerTime">06.01.2021 02:31</td>
          <td style="display:none" class="userTime">05.31.2021 21:31</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1622051820000"
            closeTime="1622514660000"
            tradeOid="h11558090415"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.77434</td>
          <td>0.77451</td>
          <td>
            <span class="green">1.7</span>
          </td>
          <td class="green">0.17</td>
          <td>5d</td>
          <td>
            <span class="green">0.00%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11558090415"
            data-type="h"
            id="commentPopOverhtradingActivity11558090415"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11558090408"
          data-record="11558090408"
          data-oid="htradingActivity11558090408"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11558090408" params="h11558090408" name="tagWindow">
            <div id="tagWindowh11558090408" class="tagWindowDiv">
              <i id="pointerh11558090408" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.25.2021 16:31</td>
          <td style="display:none" class="userTime">05.25.2021 11:31</td>

          <td class="brokerTime">06.01.2021 02:31</td>
          <td style="display:none" class="userTime">05.31.2021 21:31</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="14"
            openTime="1621960260000"
            closeTime="1622514660000"
            tradeOid="h11558090408"
            location="a"
          >
            <a
              title="EURCHF"
              href="#browserListData"
              class="underline pointer symbolName"
              >EURCHF</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>1.09734</td>
          <td>1.09871</td>
          <td>
            <span class="green">13.7</span>
          </td>
          <td class="green">1.52</td>
          <td>6d</td>
          <td>
            <span class="green">0.04%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11558090408"
            data-type="h"
            id="commentPopOverhtradingActivity11558090408"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11558090401"
          data-record="11558090401"
          data-oid="htradingActivity11558090401"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11558090401" params="h11558090401" name="tagWindow">
            <div id="tagWindowh11558090401" class="tagWindowDiv">
              <i id="pointerh11558090401" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.25.2021 10:37</td>
          <td style="display:none" class="userTime">05.25.2021 05:37</td>

          <td class="brokerTime">06.01.2021 02:31</td>
          <td style="display:none" class="userTime">05.31.2021 21:31</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1621939020000"
            closeTime="1622514660000"
            tradeOid="h11558090401"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.77673</td>
          <td>0.77447</td>
          <td>
            <span class="red">-22.6</span>
          </td>
          <td class="red">-2.26</td>
          <td>6d</td>
          <td>
            <span class="red">-0.07%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11558090401"
            data-type="h"
            id="commentPopOverhtradingActivity11558090401"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11486696568"
          data-record="11486696568"
          data-oid="htradingActivity11486696568"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11486696568" params="h11486696568" name="tagWindow">
            <div id="tagWindowh11486696568" class="tagWindowDiv">
              <i id="pointerh11486696568" class="class='red'"></i>
            </div>
          </td>
          <td class="brokerTime">05.24.2021 16:39</td>
          <td style="display:none" class="userTime">05.24.2021 11:39</td>

          <td class="brokerTime">05.25.2021 09:44</td>
          <td style="display:none" class="userTime">05.25.2021 04:44</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="14"
            openTime="1621874340000"
            closeTime="1621935840000"
            tradeOid="h11486696568"
            location="a"
          >
            <a
              title="EURCHF"
              href="#browserListData"
              class="underline pointer symbolName"
              >EURCHF</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>1.09489</td>
          <td>1.09632</td>
          <td>
            <span class="green">14.3</span>
          </td>
          <td class="green">1.60</td>
          <td>17h 5m</td>
          <td>
            <span class="green">0.05%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11486696568"
            data-type="h"
            id="commentPopOverhtradingActivity11486696568"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11486696554"
          data-record="11486696554"
          data-oid="htradingActivity11486696554"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11486696554" params="h11486696554" name="tagWindow">
            <div id="tagWindowh11486696554" class="tagWindowDiv">
              <i id="pointerh11486696554" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.24.2021 04:19</td>
          <td style="display:none" class="userTime">05.23.2021 23:19</td>

          <td class="brokerTime">05.25.2021 09:44</td>
          <td style="display:none" class="userTime">05.25.2021 04:44</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1621829940000"
            closeTime="1621935840000"
            tradeOid="h11486696554"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.77228</td>
          <td>0.77725</td>
          <td>
            <span class="green">49.7</span>
          </td>
          <td class="green">4.97</td>
          <td>1d</td>
          <td>
            <span class="green">0.15%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11486696554"
            data-type="h"
            id="commentPopOverhtradingActivity11486696554"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11486696547"
          data-record="11486696547"
          data-oid="htradingActivity11486696547"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11486696547" params="h11486696547" name="tagWindow">
            <div id="tagWindowh11486696547" class="tagWindowDiv">
              <i id="pointerh11486696547" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.21.2021 17:26</td>
          <td style="display:none" class="userTime">05.21.2021 12:26</td>

          <td class="brokerTime">05.25.2021 09:44</td>
          <td style="display:none" class="userTime">05.25.2021 04:44</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="14"
            openTime="1621617960000"
            closeTime="1621935840000"
            tradeOid="h11486696547"
            location="a"
          >
            <a
              title="EURCHF"
              href="#browserListData"
              class="underline pointer symbolName"
              >EURCHF</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>1.09507</td>
          <td>1.09633</td>
          <td>
            <span class="green">12.6</span>
          </td>
          <td class="green">1.41</td>
          <td>3d</td>
          <td>
            <span class="green">0.04%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11486696547"
            data-type="h"
            id="commentPopOverhtradingActivity11486696547"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11486696533"
          data-record="11486696533"
          data-oid="htradingActivity11486696533"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11486696533" params="h11486696533" name="tagWindow">
            <div id="tagWindowh11486696533" class="tagWindowDiv">
              <i id="pointerh11486696533" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.21.2021 09:36</td>
          <td style="display:none" class="userTime">05.21.2021 04:36</td>

          <td class="brokerTime">05.25.2021 09:44</td>
          <td style="display:none" class="userTime">05.25.2021 04:44</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1621589760000"
            closeTime="1621935840000"
            tradeOid="h11486696533"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.77488</td>
          <td>0.77721</td>
          <td>
            <span class="green">23.3</span>
          </td>
          <td class="green">2.33</td>
          <td>4d</td>
          <td>
            <span class="green">0.07%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11486696533"
            data-type="h"
            id="commentPopOverhtradingActivity11486696533"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11486696519"
          data-record="11486696519"
          data-oid="htradingActivity11486696519"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11486696519" params="h11486696519" name="tagWindow">
            <div id="tagWindowh11486696519" class="tagWindowDiv">
              <i id="pointerh11486696519" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.20.2021 11:37</td>
          <td style="display:none" class="userTime">05.20.2021 06:37</td>

          <td class="brokerTime">05.25.2021 09:44</td>
          <td style="display:none" class="userTime">05.25.2021 04:44</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1621510620000"
            closeTime="1621935840000"
            tradeOid="h11486696519"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.77489</td>
          <td>0.77721</td>
          <td>
            <span class="green">23.2</span>
          </td>
          <td class="green">2.32</td>
          <td>4d</td>
          <td>
            <span class="green">0.07%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11486696519"
            data-type="h"
            id="commentPopOverhtradingActivity11486696519"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11486696512"
          data-record="11486696512"
          data-oid="htradingActivity11486696512"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11486696512" params="h11486696512" name="tagWindow">
            <div id="tagWindowh11486696512" class="tagWindowDiv">
              <i id="pointerh11486696512" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.19.2021 04:23</td>
          <td style="display:none" class="userTime">05.18.2021 23:23</td>

          <td class="brokerTime">05.25.2021 09:44</td>
          <td style="display:none" class="userTime">05.25.2021 04:44</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1621398180000"
            closeTime="1621935840000"
            tradeOid="h11486696512"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.7784</td>
          <td>0.77731</td>
          <td>
            <span class="red">-10.9</span>
          </td>
          <td class="red">-1.09</td>
          <td>6d</td>
          <td>
            <span class="red">-0.03%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11486696512"
            data-type="h"
            id="commentPopOverhtradingActivity11486696512"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11486696505"
          data-record="11486696505"
          data-oid="htradingActivity11486696505"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11486696505" params="h11486696505" name="tagWindow">
            <div id="tagWindowh11486696505" class="tagWindowDiv">
              <i id="pointerh11486696505" class="class='red'"></i>
            </div>
          </td>
          <td class="brokerTime">05.18.2021 16:40</td>
          <td style="display:none" class="userTime">05.18.2021 11:40</td>

          <td class="brokerTime">05.25.2021 09:44</td>
          <td style="display:none" class="userTime">05.25.2021 04:44</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="14"
            openTime="1621356000000"
            closeTime="1621935840000"
            tradeOid="h11486696505"
            location="a"
          >
            <a
              title="EURCHF"
              href="#browserListData"
              class="underline pointer symbolName"
              >EURCHF</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>1.09566</td>
          <td>1.09636</td>
          <td>
            <span class="green">7.0</span>
          </td>
          <td class="green">0.78</td>
          <td>6d</td>
          <td>
            <span class="green">0.02%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11486696505"
            data-type="h"
            id="commentPopOverhtradingActivity11486696505"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11486696498"
          data-record="11486696498"
          data-oid="htradingActivity11486696498"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11486696498" params="h11486696498" name="tagWindow">
            <div id="tagWindowh11486696498" class="tagWindowDiv">
              <i id="pointerh11486696498" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.18.2021 11:13</td>
          <td style="display:none" class="userTime">05.18.2021 06:13</td>

          <td class="brokerTime">05.25.2021 09:44</td>
          <td style="display:none" class="userTime">05.25.2021 04:44</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1621336380000"
            closeTime="1621935840000"
            tradeOid="h11486696498"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.77992</td>
          <td>0.77733</td>
          <td>
            <span class="red">-25.9</span>
          </td>
          <td class="red">-2.59</td>
          <td>6d</td>
          <td>
            <span class="red">-0.08%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11486696498"
            data-type="h"
            id="commentPopOverhtradingActivity11486696498"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11464100827"
          data-record="11464100827"
          data-oid="htradingActivity11464100827"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11464100827" params="h11464100827" name="tagWindow">
            <div id="tagWindowh11464100827" class="tagWindowDiv">
              <i id="pointerh11464100827" class="class='red'"></i>
            </div>
          </td>
          <td class="brokerTime">05.13.2021 07:16</td>
          <td style="display:none" class="userTime">05.13.2021 02:16</td>

          <td class="brokerTime">05.18.2021 09:51</td>
          <td style="display:none" class="userTime">05.18.2021 04:51</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1620890160000"
            closeTime="1621331460000"
            tradeOid="h11464100827"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.77189</td>
          <td>0.78055</td>
          <td>
            <span class="green">86.6</span>
          </td>
          <td class="green">8.66</td>
          <td>5d</td>
          <td>
            <span class="green">0.26%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11464100827"
            data-type="h"
            id="commentPopOverhtradingActivity11464100827"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11464100826"
          data-record="11464100826"
          data-oid="htradingActivity11464100826"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11464100826" params="h11464100826" name="tagWindow">
            <div id="tagWindowh11464100826" class="tagWindowDiv">
              <i id="pointerh11464100826" class="class='green'"></i>
            </div>
          </td>
          <td class="brokerTime">05.12.2021 03:48</td>
          <td style="display:none" class="userTime">05.11.2021 22:48</td>

          <td class="brokerTime">05.18.2021 09:51</td>
          <td style="display:none" class="userTime">05.18.2021 04:51</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1620791280000"
            closeTime="1621331460000"
            tradeOid="h11464100826"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.78262</td>
          <td>0.78056</td>
          <td>
            <span class="red">-20.6</span>
          </td>
          <td class="red">-2.06</td>
          <td>6d</td>
          <td>
            <span class="red">-0.06%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11464100826"
            data-type="h"
            id="commentPopOverhtradingActivity11464100826"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11464100825"
          data-record="11464100825"
          data-oid="htradingActivity11464100825"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11464100825" params="h11464100825" name="tagWindow">
            <div id="tagWindowh11464100825" class="tagWindowDiv">
              <i id="pointerh11464100825" class="class='red'"></i>
            </div>
          </td>
          <td class="brokerTime">05.11.2021 03:56</td>
          <td style="display:none" class="userTime">05.10.2021 22:56</td>

          <td class="brokerTime">05.18.2021 09:51</td>
          <td style="display:none" class="userTime">05.18.2021 04:51</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1620705360000"
            closeTime="1621331460000"
            tradeOid="h11464100825"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.78262</td>
          <td>0.78057</td>
          <td>
            <span class="red">-20.5</span>
          </td>
          <td class="red">-2.05</td>
          <td>7d</td>
          <td>
            <span class="red">-0.06%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11464100825"
            data-type="h"
            id="commentPopOverhtradingActivity11464100825"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11464100824"
          data-record="11464100824"
          data-oid="htradingActivity11464100824"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11464100824" params="h11464100824" name="tagWindow">
            <div id="tagWindowh11464100824" class="tagWindowDiv">
              <i id="pointerh11464100824" class="class='red'"></i>
            </div>
          </td>
          <td class="brokerTime">05.10.2021 05:48</td>
          <td style="display:none" class="userTime">05.10.2021 00:48</td>

          <td class="brokerTime">05.18.2021 09:51</td>
          <td style="display:none" class="userTime">05.18.2021 04:51</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1620625680000"
            closeTime="1621331460000"
            tradeOid="h11464100824"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.78407</td>
          <td>0.78053</td>
          <td>
            <span class="red">-35.4</span>
          </td>
          <td class="red">-3.54</td>
          <td>8d</td>
          <td>
            <span class="red">-0.10%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11464100824"
            data-type="h"
            id="commentPopOverhtradingActivity11464100824"
          ></td>
        </tr>
        <tr
          class="commentRow  "
          id="commentRowhtradingActivity11464100823"
          data-record="11464100823"
          data-oid="htradingActivity11464100823"
          data-accountoid="1152318"
          data-type="h"
        >
          <td id="tagTdh11464100823" params="h11464100823" name="tagWindow">
            <div id="tagWindowh11464100823" class="tagWindowDiv">
              <i id="pointerh11464100823" class="class='red'"></i>
            </div>
          </td>
          <td class="brokerTime">05.14.2021 03:28</td>
          <td style="display:none" class="userTime">05.13.2021 22:28</td>

          <td class="brokerTime">05.18.2021 09:50</td>
          <td style="display:none" class="userTime">05.18.2021 04:50</td>
          <td
            class="symbol"
            getTradeConfig="true"
            accountOid="1152318"
            tradeSymbolOid="11"
            openTime="1620962880000"
            closeTime="1621331400000"
            tradeOid="h11464100823"
            location="a"
          >
            <a
              title="AUDUSD"
              href="#browserListData"
              class="underline pointer symbolName"
              >AUDUSD</a
            >
          </td>
          <td>Buy</td>
          <td>0.01</td>
          <td>0.77162</td>
          <td>0.78055</td>
          <td>
            <span class="green">89.3</span>
          </td>
          <td class="green">8.93</td>
          <td>4d</td>
          <td>
            <span class="green">0.26%</span>
          </td>
          <td class="sparkline">-</td>
          <td
            name="commentModal"
            data-oid="htradingActivity11464100823"
            data-type="h"
            id="commentPopOverhtradingActivity11464100823"
          ></td>
        </tr>
      </tbody>
    </table>
  </div>
</div>

<input type="hidden" value="1640" name="totalCount" />
<div class="pagination-container">
  <div>
    <ul
      class="pagination responsive-paging"
      container="historyCont"
      history="false"
      reloadAds="false"
      scrollToTop="false"
    >
      <li class="prev">
        <a
          href="javascript:void(0);"
          class="btn disabled-a"
          onclick="return false;"
          title="Prev"
        >
          <i class="fas fa-angle-left"></i>
        </a>
      </li>
      <li class="active">
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=1&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="1"
        >
          1
        </a>
      </li>
      <li>
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=2&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="2"
        >
          2
        </a>
      </li>
      <li>
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=3&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="3"
        >
          3
        </a>
      </li>
      <li>
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=4&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="4"
        >
          4
        </a>
      </li>
      <li>
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=5&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="5"
        >
          5
        </a>
      </li>
      <li>
        <a class="btn disabled-a bold">..</a>
      </li>
      <li>
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=82&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="82"
          lastPage="true"
        >
          82
        </a>
      </li>
      <li class="next">
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=2&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="2"
          title="Next"
        >
          <i class="fas fa-angle-right"></i>
        </a>
      </li>
    </ul>

    <ul
      class="pagination responsive-paging mobile-paging"
      container="historyCont"
      history="false"
      reloadAds="false"
      scrollToTop="false"
      style="display: none;"
    >
      <li class="prev">
        <a
          href="javascript:void(0);"
          class="btn disabled-a"
          onclick="return false;"
          title="Prev"
        >
          <i class="fas fa-angle-left"></i>
        </a>
      </li>
      <li class="active">
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=1&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="1"
        >
          1
        </a>
      </li>
      <li>
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=2&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="2"
        >
          2
        </a>
      </li>
      <li>
        <a class="btn disabled-a bold">..</a>
      </li>
      <li>
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=81&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="81"
        >
          81
        </a>
      </li>
      <li>
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=82&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="82"
          lastPage="true"
        >
          82
        </a>
      </li>
      <li class="next">
        <a
          href="javascript:void(0);"
          class="btn paging-btn"
          params="?pt=4&p=2&ts=1640&&id=1152318&l=a&invitation=&start=2015-01-05 00:00&end=2021-06-14 06:00&sb=28&st=2&magicNumbers=&symbols=&types=0,1,2,4,19,5&orderTagList=&daysList=&hoursList=&buySellList=&yieldStart=&yieldEnd=&netProfitStart=&netProfitEnd=&durationStart=&durationEnd=&takeProfitStart=&takeProfitEnd=&stopLoss=&stopLossEnd=&sizingStart=&sizingEnd=&selectedTime=&pipsStart=&pipsEnd=&ts=1640"
          page="2"
          title="Next"
        >
          <i class="fas fa-angle-right"></i>
        </a>
      </li>
    </ul>
  </div>
</div>
```

E o que importa para gente são as TRs:

```html
<tr
  class="commentRow  "
  id="commentRowhtradingActivity11558090443"
  data-record="11558090443"
  data-oid="htradingActivity11558090443"
  data-accountoid="1152318"
  data-type="h"
>
  <td id="tagTdh11558090443" params="h11558090443" name="tagWindow">
    <div id="tagWindowh11558090443" class="tagWindowDiv">
      <i id="pointerh11558090443" class="$class"></i>
    </div>
  </td>
  <td class="brokerTime">05.31.2021 03:33</td>
  <td style="display:none" class="userTime">05.30.2021 22:33</td>

  <td class="brokerTime">06.01.2021 02:31</td>
  <td style="display:none" class="userTime">05.31.2021 21:31</td>
  <td
    class="symbol"
    gettradeconfig="true"
    accountoid="1152318"
    tradesymboloid="11"
    opentime="1622431980000"
    closetime="1622514660000"
    tradeoid="h11558090443"
    location="a"
  >
    <a
      title="AUDUSD"
      href="#browserListData"
      class="underline pointer symbolName"
      >AUDUSD</a
    >
  </td>
  <td>Buy</td>
  <td>0.01</td>
  <td>0.77041</td>
  <td>0.77451</td>
  <td>
    <span class="green">41.0</span>
  </td>
  <td class="green">4.10</td>
  <td>22h 58m</td>
  <td>
    <span class="green">0.12%</span>
  </td>
  <td class="sparkline">-</td>
  <td
    name="commentModal"
    data-oid="htradingActivity11558090443"
    data-type="h"
    id="commentPopOverhtradingActivity11558090443"
  ></td>
</tr>
```

Para cada TR devemos extrair (em ordem dos TDs):

- Open Date
- Close Date
- Symbol
- Action
- Lots
- Open Price
- Close Price
- Pips
- Profit (USD)
- Duration
- Gain

Algumas linhas podem ser "especiais" (ex: deposit e withdrawal), então podemos ignorar aqui (ou não, decida sobre isso). Exemplo:

```html
<tr
  class="commentRow orange "
  id="commentRowhtradingActivity787028189"
  data-record="787028189"
  data-oid="htradingActivity787028189"
  data-accountoid="1152318"
  data-type="h"
>
  <td id="tagTdh787028189" params="h787028189" name="tagWindow">
    <div id="tagWindowh787028189" class="tagWindowDiv">
      <i id="pointerh787028189" class="class='red'"></i>
    </div>
  </td>
  <td class="brokerTime">01.05.2015 11:32</td>
  <td style="display:none" class="userTime">01.05.2015 06:32</td>

  <td class="brokerTime"></td>
  <td style="display:none" class="userTime"></td>
  <td
    class="symbol"
    gettradeconfig=" false"
    accountoid="1152318"
    tradesymboloid=""
    opentime="1420457520000"
    closetime="1420457520000"
    tradeoid="h787028189"
    location="a"
  ></td>
  <td>Deposit</td>
  <td></td>
  <td></td>
  <td></td>
  <td></td>
  <td class="green">1,068.00</td>
  <td></td>
  <td></td>
  <td class="sparkline"></td>
  <td
    name="commentModal"
    data-oid="htradingActivity787028189"
    data-type="h"
    id="commentPopOverhtradingActivity787028189"
  ></td>
</tr>
```

# Objetivo final

Para cada system extrair 1) json com os dados do system e 2) csv/parquet com os dados do trade history.

Com isso nós vamos prosseguir para a "engenharia reserva" para decodificar a estratégia/sinais desse trader.

Faça o código em python, dentro da pasta: studies/myfxbook_reverse_engineering

Verifique se já existe algo dentro da pasta que possa ser reaproveitado.
