--------------------------------------------------------------------------------
-- tb_spi.vhd
-- ЛР3 АПКС, варіант 15 (SPI, VHDL). Процак М.С., КІ-402.
--
-- Тестбенч функціональної верифікації SPI Master.
-- Імітує зовнішнє середовище:
--   * генерація CLK (50 МГц) і RESET;
--   * подача тестових слів на вхід передавача Master (tx_data/start);
--   * SPI Slave (spi_slave) імітує інший пристрій і передає власні слова
--     по MISO — так перевіряється приймач Master;
--   * незалежний монітор шини відновлює слова з ліній MOSI/MISO за
--     специфікацією SPI (CPOL/CPHA) — перевірка бітового потоку передавача;
--   * перевірка рівня SCLK у стані спокою і кількості фронтів у кадрі.
-- Режим SPI задається generic-параметрами (запуск для режимів 0..3).
-- Кінець симуляції: std.env.finish; при помилках - assertion failure.
--------------------------------------------------------------------------------
library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use std.env.all;

entity tb_spi is
  generic (
    CPOL : std_logic := '0';
    CPHA : std_logic := '0'
  );
end entity;

architecture sim of tb_spi is
  constant DATA_W   : positive := 8;
  constant CLK_DIV  : positive := 4;          -- SCLK = 50 МГц / 8 = 6.25 МГц
  constant T_CLK    : time     := 20 ns;      -- 50 МГц

  type word_arr is array (natural range <>) of std_logic_vector(DATA_W-1 downto 0);
  -- тестові вектори: граничні (00, FF), чергування бітів (A5/5A, 55/AA), окремі біти (01, 80)
  constant M_TX : word_arr := (x"A5", x"3C", x"FF", x"00", x"81", x"5A", x"01", x"80");
  constant S_TX : word_arr := (x"C3", x"96", x"00", x"FF", x"7E", x"A5", x"80", x"01");

  signal clk      : std_logic := '0';
  signal rst      : std_logic := '1';
  signal start    : std_logic := '0';
  signal m_txd    : std_logic_vector(DATA_W-1 downto 0) := (others => '0');
  signal m_rxd    : std_logic_vector(DATA_W-1 downto 0);
  signal m_rxv    : std_logic;
  signal busy     : std_logic;
  signal s_txd    : std_logic_vector(DATA_W-1 downto 0) := (others => '0');
  signal s_rxd    : std_logic_vector(DATA_W-1 downto 0);
  signal s_rxv    : std_logic;
  signal sclk, mosi, miso, ss_n : std_logic;

  -- результати монітора шини
  signal mon_mosi, mon_miso : std_logic_vector(DATA_W-1 downto 0) := (others => '0');
  signal mon_done : natural := 0;           -- кількість відновлених кадрів
  signal mon_edges : natural := 0;          -- фронтів SCLK у останньому кадрі
  signal errors   : natural := 0;
  signal sim_done : boolean := false;
begin

  -- генерація тактового сигналу
  clk <= not clk after T_CLK/2 when not sim_done else '0';

  -- пристрій, що перевіряється
  dut : entity work.spi_master
    generic map (DATA_W => DATA_W, CLK_DIV => CLK_DIV, CPOL => CPOL, CPHA => CPHA)
    port map (clk => clk, rst => rst, start => start, tx_data => m_txd,
              rx_data => m_rxd, rx_valid => m_rxv, busy => busy,
              sclk => sclk, mosi => mosi, miso => miso, ss_n => ss_n);

  -- інший пристрій на шині
  slave : entity work.spi_slave
    generic map (DATA_W => DATA_W, CPOL => CPOL, CPHA => CPHA)
    port map (clk => clk, rst => rst, sclk => sclk, ss_n => ss_n, mosi => mosi,
              miso => miso, tx_data => s_txd, rx_data => s_rxd, rx_valid => s_rxv);

  ------------------------------------------------------------------------------
  -- Монітор шини: відновлює слова з MOSI/MISO незалежно від DUT.
  -- Біт фіксується на фронті SCLK: CPOL xor CPHA = 0 -> наростаючий, 1 -> спадаючий.
  ------------------------------------------------------------------------------
  monitor : process
    variable vm, vs : std_logic_vector(DATA_W-1 downto 0);
    variable n_edges : natural;
  begin
    wait until falling_edge(ss_n);
    n_edges := 0;
    for i in DATA_W-1 downto 0 loop
      if (CPOL xor CPHA) = '0' then
        wait until rising_edge(sclk);
      else
        wait until falling_edge(sclk);
      end if;
      vm(i) := mosi;
      vs(i) := miso;
    end loop;
    wait until rising_edge(ss_n);
    mon_mosi <= vm;
    mon_miso <= vs;
    mon_done <= mon_done + 1;
  end process;

  -- лічильник фронтів SCLK у кадрі (має бути 2*DATA_W)
  edge_count : process
    variable n : natural;
  begin
    wait until falling_edge(ss_n);
    n := 0;
    loop
      wait on sclk, ss_n;
      exit when ss_n = '1';
      if sclk'event then n := n + 1; end if;
    end loop;
    mon_edges <= n;
  end process;

  -- SCLK у стані спокою (SS_N = 1) має дорівнювати CPOL
  idle_check : process (clk)
  begin
    if rising_edge(clk) then
      if rst = '0' and ss_n = '1' and sclk /= CPOL then
        report "SCLK idle level /= CPOL" severity error;
      end if;
    end if;
  end process;

  ------------------------------------------------------------------------------
  -- Сценарій тесту
  ------------------------------------------------------------------------------
  stim : process
    variable err : natural := 0;
    procedure check(cond : boolean; msg : string) is
    begin
      if not cond then
        err := err + 1;
        report "FAIL: " & msg severity error;
      end if;
    end procedure;
  begin
    report "=== SPI test, mode " & integer'image(to_integer(unsigned'(CPOL & CPHA))) &
           " (CPOL=" & std_logic'image(CPOL) & ", CPHA=" & std_logic'image(CPHA) & ")";
    rst <= '1';
    wait for 5 * T_CLK;
    wait until rising_edge(clk);
    rst <= '0';
    wait for 3 * T_CLK;

    for k in M_TX'range loop
      -- підготовка даних: Master передає M_TX(k), Slave відповідає S_TX(k)
      wait until rising_edge(clk);
      m_txd <= M_TX(k);
      s_txd <= S_TX(k);
      start <= '1';
      wait until rising_edge(clk);
      start <= '0';
      wait for 1 ns;                                           -- після оновлення регістрів на фронті
      check(busy = '1', "busy not asserted after start");

      wait until rising_edge(clk) and m_rxv = '1';             -- Master прийняв слово
      check(m_rxd = S_TX(k), "master RX: got " & to_hstring(m_rxd) & ", expected " & to_hstring(S_TX(k)));
      wait until rising_edge(clk) and s_rxv = '1';             -- Slave прийняв слово
      check(s_rxd = M_TX(k), "slave RX: got " & to_hstring(s_rxd) & ", expected " & to_hstring(M_TX(k)));
      wait for T_CLK;
      check(mon_done = k + 1, "bus monitor frame count");
      check(mon_mosi = M_TX(k), "MOSI stream: got " & to_hstring(mon_mosi) & ", expected " & to_hstring(M_TX(k)));
      check(mon_miso = S_TX(k), "MISO stream: got " & to_hstring(mon_miso) & ", expected " & to_hstring(S_TX(k)));
      check(mon_edges = 2*DATA_W, "SCLK edges per frame: " & integer'image(mon_edges));
      check(busy = '0', "busy still asserted after frame");
      report "frame " & integer'image(k) & ": master TX " & to_hstring(M_TX(k)) &
             " -> slave RX " & to_hstring(s_rxd) & " | slave TX " & to_hstring(S_TX(k)) &
             " -> master RX " & to_hstring(m_rxd);
      wait for 10 * T_CLK;                                     -- пауза між кадрами
    end loop;

    -- скидання посеред кадру: шина має повернутися в стан спокою
    wait until rising_edge(clk);
    m_txd <= x"F0"; start <= '1';
    wait until rising_edge(clk);
    start <= '0';
    wait for 20 * T_CLK;
    rst <= '1';
    wait until rising_edge(clk);
    wait until rising_edge(clk);
    check(ss_n = '1' and sclk = CPOL and busy = '0', "bus not idle after reset");
    rst <= '0';
    wait for 10 * T_CLK;

    errors <= err;
    if err = 0 then
      report "=== RESULT: PASS (" & integer'image(M_TX'length) & " frames, mode " &
             integer'image(to_integer(unsigned'(CPOL & CPHA))) & ")";
    else
      report "=== RESULT: FAIL, errors = " & integer'image(err) severity failure;
    end if;
    sim_done <= true;
    finish;
  end process;

end architecture;
