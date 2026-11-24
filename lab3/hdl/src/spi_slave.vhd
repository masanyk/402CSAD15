--------------------------------------------------------------------------------
-- spi_slave.vhd
-- ЛР3 АПКС, варіант 15 (SPI, VHDL). Процак М.С., КІ-402.
--
-- SPI Slave — «інший пристрій» на шині, з яким обмінюється даними Master.
-- Синтезовна модель, що працює від власного системного такту clk
-- (умова: f_clk >= 4 * f_sclk). Лінії SCLK, SS_N, MOSI проходять через
-- двотригерні синхронізатори, фронти SCLK визначаються в домені clk.
--
-- Логіка (та сама, що й у Master, відповідно до CPOL/CPHA):
--   * спад SS_N: завантажити tx_data, MISO = старший біт;
--   * фронт фіксації: вдвинути MOSI у приймальний регістр;
--   * фронт зміни: висунути наступний біт на MISO (лише після фіксації попереднього);
--   * підйом SS_N: видати прийняте слово rx_data і строб rx_valid.
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;

entity spi_slave is
  generic (
    DATA_W : positive  := 8;
    CPOL   : std_logic := '0';
    CPHA   : std_logic := '0'
  );
  port (
    clk      : in  std_logic;                            -- системний такт slave
    rst      : in  std_logic;                            -- синхронне скидання
    sclk     : in  std_logic;                            -- лінії SPI від Master
    ss_n     : in  std_logic;
    mosi     : in  std_logic;
    miso     : out std_logic;
    tx_data  : in  std_logic_vector(DATA_W-1 downto 0);  -- слово-відповідь для Master
    rx_data  : out std_logic_vector(DATA_W-1 downto 0);  -- слово, прийняте від Master
    rx_valid : out std_logic                             -- '1' один такт після підйому SS_N
  );
end entity;

architecture rtl of spi_slave is
  -- двотригерні синхронізатори (індекс 0 - перший тригер, 1 - другий), 2 - затримана копія
  signal sclk_s : std_logic_vector(2 downto 0) := (others => CPOL);
  signal ss_s   : std_logic_vector(2 downto 0) := (others => '1');
  signal mosi_s : std_logic_vector(1 downto 0) := (others => '0');

  signal tx_sh  : std_logic_vector(DATA_W-1 downto 0) := (others => '0'); -- регістр відповіді
  signal rx_sh  : std_logic_vector(DATA_W-1 downto 0) := (others => '0'); -- приймальний регістр
  signal rx_r   : std_logic_vector(DATA_W-1 downto 0) := (others => '0');
  signal vld_r  : std_logic := '0';
  signal nbits  : natural range 0 to DATA_W := 0;                         -- кількість прийнятих бітів
begin

  process (clk)
    variable edge, lead, smp : boolean;
  begin
    if rising_edge(clk) then
      vld_r <= '0';
      sclk_s <= sclk_s(1 downto 0) & sclk;
      ss_s   <= ss_s(1 downto 0) & ss_n;
      mosi_s <= mosi_s(0) & mosi;

      if rst = '1' then
        tx_sh <= (others => '0');
        rx_sh <= (others => '0');
        rx_r  <= (others => '0');
        nbits <= 0;
      elsif ss_s(2) = '1' and ss_s(1) = '0' then         -- спад SS_N: початок кадру
        tx_sh <= tx_data;
        rx_sh <= (others => '0');
        nbits <= 0;
      elsif ss_s(2) = '0' and ss_s(1) = '1' then         -- підйом SS_N: кінець кадру
        rx_r  <= rx_sh;
        vld_r <= '1';
      elsif ss_s(1) = '0' then
        edge := sclk_s(2) /= sclk_s(1);
        if edge then
          lead := sclk_s(2) = CPOL;                      -- вихід зі стану спокою = передній фронт
          smp  := (lead and CPHA = '0') or ((not lead) and CPHA = '1');
          if smp then
            rx_sh <= rx_sh(DATA_W-2 downto 0) & mosi_s(1);
            nbits <= nbits + 1;
          elsif nbits > 0 and nbits < DATA_W then
            tx_sh <= tx_sh(DATA_W-2 downto 0) & '0';
          end if;
        end if;
      end if;
    end if;
  end process;

  -- MISO у третьому стані, коли slave не вибраний (для спільної шини)
  miso     <= tx_sh(DATA_W-1) when ss_n = '0' else 'Z';
  rx_data  <= rx_r;
  rx_valid <= vld_r;

end architecture;
