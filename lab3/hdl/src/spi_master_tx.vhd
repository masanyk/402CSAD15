--------------------------------------------------------------------------------
-- spi_master_tx.vhd
-- ЛР3 АПКС, варіант 15 (SPI, VHDL). Процак М.С., КІ-402.
--
-- Передавач SPI Master: керуючий автомат (FSM), дільник тактової частоти,
-- генерація SCLK і SS_N, видача даних на MOSI (старшим бітом вперед, MSB first).
-- Режим SPI задається generic-параметрами CPOL/CPHA (режими 0..3).
--
-- Для приймача (spi_master_rx) формуються строби:
--   sample_o  - один такт clk у момент фронту SCLK, на якому треба фіксувати MISO;
--   start_o   - початок транзакції (очистити приймач);
--   done_o    - транзакцію завершено (усі DATA_W бітів передано і прийнято).
--
-- Часова діаграма (CPHA = 0):
--   SS_N  ‾‾\____________________________________/‾‾
--   SCLK  ____/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\_/‾\______   (CPOL = 0)
--   MOSI  ==X b7 X b6 X b5 X b4 X b3 X b2 X b1 X b0 X==
--              ^ фіксація на передньому фронті, зміна на задньому
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity spi_master_tx is
  generic (
    DATA_W  : positive := 8;   -- розрядність слова
    CLK_DIV : positive := 4;   -- тактів clk на половину періоду SCLK: f_sclk = f_clk / (2*CLK_DIV)
    CPOL    : std_logic := '0';-- рівень SCLK у стані спокою
    CPHA    : std_logic := '0' -- 0: фіксація на передньому фронті, 1: на задньому
  );
  port (
    clk      : in  std_logic;                            -- системний такт
    rst      : in  std_logic;                            -- синхронне скидання, активний '1'
    start    : in  std_logic;                            -- запуск транзакції (імпульс 1 такт)
    tx_data  : in  std_logic_vector(DATA_W-1 downto 0);  -- слово для передачі
    busy     : out std_logic;                            -- '1' поки триває транзакція
    sclk     : out std_logic;                            -- тактовий сигнал SPI
    mosi     : out std_logic;                            -- Master Out Slave In
    ss_n     : out std_logic;                            -- вибір пристрою, активний '0'
    sample_o : out std_logic;                            -- строб фіксації MISO для приймача
    start_o  : out std_logic;                            -- строб початку транзакції
    done_o   : out std_logic                             -- строб завершення транзакції
  );
end entity;

architecture rtl of spi_master_tx is
  -- Стани автомата передавача
  --   IDLE     - спокій: SS_N = 1, SCLK = CPOL
  --   SETUP    - SS_N = 0, витримка половини періоду до першого фронту SCLK
  --   TRANSFER - генерація 2*DATA_W фронтів SCLK, зсув MOSI, строби фіксації
  --   HOLD     - витримка половини періоду після останнього фронту перед зняттям SS_N
  --   FINISH   - SS_N = 1, видача строба done_o, повернення в IDLE
  type state_t is (IDLE, SETUP, TRANSFER, HOLD, FINISH);
  signal state    : state_t := IDLE;

  signal div_cnt  : natural range 0 to CLK_DIV-1 := 0;        -- лічильник дільника частоти
  signal edge_cnt : natural range 0 to 2*DATA_W := 0;         -- кількість сформованих фронтів SCLK
  signal bits_smp : natural range 0 to DATA_W := 0;           -- кількість зафіксованих бітів
  signal shreg    : std_logic_vector(DATA_W-1 downto 0) := (others => '0'); -- зсувний регістр MOSI
  signal sclk_r   : std_logic := CPOL;                        -- внутрішній SCLK
  signal ss_r     : std_logic := '1';
  signal sample_r, start_r, done_r : std_logic := '0';
begin

  process (clk)
    variable lead      : boolean;  -- поточний фронт SCLK є переднім (виходом зі стану спокою)
    variable is_sample : boolean;  -- на цьому фронті фіксується біт
  begin
    if rising_edge(clk) then
      sample_r <= '0';
      start_r  <= '0';
      done_r   <= '0';

      if rst = '1' then
        state    <= IDLE;
        div_cnt  <= 0;
        edge_cnt <= 0;
        bits_smp <= 0;
        sclk_r   <= CPOL;
        ss_r     <= '1';
        shreg    <= (others => '0');
      else
        case state is

          when IDLE =>
            sclk_r <= CPOL;
            ss_r   <= '1';
            if start = '1' then
              shreg    <= tx_data;   -- MOSI одразу показує старший біт
              ss_r     <= '0';
              div_cnt  <= 0;
              edge_cnt <= 0;
              bits_smp <= 0;
              start_r  <= '1';
              state    <= SETUP;
            end if;

          when SETUP =>               -- t_setup = половина періоду SCLK
            if div_cnt = CLK_DIV-1 then
              div_cnt <= 0;
              state   <= TRANSFER;
            else
              div_cnt <= div_cnt + 1;
            end if;

          when TRANSFER =>
            if div_cnt = CLK_DIV-1 then
              div_cnt   <= 0;
              sclk_r    <= not sclk_r;                 -- черговий фронт SCLK
              edge_cnt  <= edge_cnt + 1;
              lead      := (edge_cnt mod 2 = 0);
              -- CPHA=0: фіксація на передніх фронтах; CPHA=1: на задніх
              is_sample := (lead and CPHA = '0') or ((not lead) and CPHA = '1');
              if is_sample then
                sample_r <= '1';
                bits_smp <= bits_smp + 1;
              elsif bits_smp > 0 and bits_smp < DATA_W then
                -- фронт зміни даних: наступний біт на MOSI (лише після фіксації попереднього)
                shreg <= shreg(DATA_W-2 downto 0) & '0';
              end if;
              if edge_cnt = 2*DATA_W-1 then           -- це був останній фронт
                state <= HOLD;
              end if;
            else
              div_cnt <= div_cnt + 1;
            end if;

          when HOLD =>                -- t_hold = половина періоду SCLK
            if div_cnt = CLK_DIV-1 then
              div_cnt <= 0;
              state   <= FINISH;
            else
              div_cnt <= div_cnt + 1;
            end if;

          when FINISH =>
            ss_r   <= '1';
            done_r <= '1';
            state  <= IDLE;

        end case;
      end if;
    end if;
  end process;

  busy     <= '0' when state = IDLE else '1';
  sclk     <= sclk_r;
  ss_n     <= ss_r;
  mosi     <= shreg(DATA_W-1) when ss_r = '0' else '0';
  sample_o <= sample_r;
  start_o  <= start_r;
  done_o   <= done_r;

end architecture;
