--------------------------------------------------------------------------------
-- spi_master_rx.vhd
-- ЛР3 АПКС, варіант 15 (SPI, VHDL). Процак М.С., КІ-402.
--
-- Приймач SPI Master. Логіка роботи:
--   1. За стробом start_i очищає зсувний регістр.
--   2. Кожен строб sample_i (формує передавач на фронті фіксації SCLK відповідно
--      до CPHA) вдвигає поточне значення MISO у молодший розряд регістра
--      (дані надходять старшим бітом вперед).
--   3. За стробом done_i прийняте слово переноситься у вихідний регістр rx_data
--      і на один такт виставляється rx_valid.
-- MISO синхронізується двома тригерами не потрібно: його фіксація відбувається
-- через половину періоду SCLK після зміни, тобто дані вже стабільні.
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;

entity spi_master_rx is
  generic (
    DATA_W : positive := 8
  );
  port (
    clk      : in  std_logic;                            -- системний такт
    rst      : in  std_logic;                            -- синхронне скидання
    miso     : in  std_logic;                            -- Master In Slave Out
    start_i  : in  std_logic;                            -- початок транзакції
    sample_i : in  std_logic;                            -- строб фіксації біта
    done_i   : in  std_logic;                            -- кінець транзакції
    rx_data  : out std_logic_vector(DATA_W-1 downto 0);  -- прийняте слово
    rx_valid : out std_logic                             -- '1' один такт: rx_data оновлено
  );
end entity;

architecture rtl of spi_master_rx is
  signal shreg  : std_logic_vector(DATA_W-1 downto 0) := (others => '0'); -- зсувний регістр MISO
  signal data_r : std_logic_vector(DATA_W-1 downto 0) := (others => '0'); -- вихідний регістр
  signal vld_r  : std_logic := '0';
begin

  process (clk)
  begin
    if rising_edge(clk) then
      vld_r <= '0';
      if rst = '1' then
        shreg  <= (others => '0');
        data_r <= (others => '0');
      else
        if start_i = '1' then
          shreg <= (others => '0');
        elsif sample_i = '1' then
          shreg <= shreg(DATA_W-2 downto 0) & miso;   -- MSB first
        end if;
        if done_i = '1' then
          data_r <= shreg;
          vld_r  <= '1';
        end if;
      end if;
    end if;
  end process;

  rx_data  <= data_r;
  rx_valid <= vld_r;

end architecture;
