--------------------------------------------------------------------------------
-- spi_master.vhd
-- ЛР3 АПКС, варіант 15 (SPI, VHDL). Процак М.С., КІ-402.
--
-- Верхній модуль SPI Master: об'єднує передавач (spi_master_tx) і приймач
-- (spi_master_rx). Повнодуплексний обмін: за одну транзакцію передається
-- tx_data по MOSI і одночасно приймається слово по MISO.
--
--          +---------------- spi_master ----------------+
--  start ->|  +---------------+   sample/start/done     |
-- tx_data->|  | spi_master_tx |----------------+         |-> sclk, mosi, ss_n
--  busy  <-|  +---------------+                v         |
--          |                         +---------------+   |<- miso
-- rx_data<-|                         | spi_master_rx |   |
-- rx_valid<|                         +---------------+   |
--          +---------------------------------------------+
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;

entity spi_master is
  generic (
    DATA_W  : positive  := 8;
    CLK_DIV : positive  := 4;    -- f_sclk = f_clk / (2*CLK_DIV); 50 МГц / 8 = 6.25 МГц
    CPOL    : std_logic := '0';
    CPHA    : std_logic := '0'
  );
  port (
    clk      : in  std_logic;
    rst      : in  std_logic;
    -- користувацький інтерфейс
    start    : in  std_logic;
    tx_data  : in  std_logic_vector(DATA_W-1 downto 0);
    rx_data  : out std_logic_vector(DATA_W-1 downto 0);
    rx_valid : out std_logic;
    busy     : out std_logic;
    -- лінії SPI
    sclk     : out std_logic;
    mosi     : out std_logic;
    miso     : in  std_logic;
    ss_n     : out std_logic
  );
end entity;

architecture rtl of spi_master is
  signal sample_s, start_s, done_s : std_logic;
begin

  u_tx : entity work.spi_master_tx
    generic map (DATA_W => DATA_W, CLK_DIV => CLK_DIV, CPOL => CPOL, CPHA => CPHA)
    port map (
      clk => clk, rst => rst, start => start, tx_data => tx_data, busy => busy,
      sclk => sclk, mosi => mosi, ss_n => ss_n,
      sample_o => sample_s, start_o => start_s, done_o => done_s);

  u_rx : entity work.spi_master_rx
    generic map (DATA_W => DATA_W)
    port map (
      clk => clk, rst => rst, miso => miso,
      start_i => start_s, sample_i => sample_s, done_i => done_s,
      rx_data => rx_data, rx_valid => rx_valid);

end architecture;
