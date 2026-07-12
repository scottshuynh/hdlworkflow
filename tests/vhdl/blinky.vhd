library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.standard_pkg.all;

entity blinky is
  generic (
    led_toggle_period_cycles : natural := 100_000_000
  );
  port (
    clk_i : in  std_logic;
    led_o : out std_logic
  );
end entity;

architecture rtl of blinky is
  constant COUNT_W  : natural := ceil_log2(led_toggle_period_cycles);
  signal count      : unsigned(COUNT_W - 1 downto 0) := (others => '0');
  signal next_count : unsigned(COUNT_W - 1 downto 0);
  signal led        : std_logic := '0';
begin

  process (clk_i)
  begin
    if rising_edge(clk_i) then
      count <= count + 1;
      if next_count = led_toggle_period_cycles then
        led <= not led;
        count <= (others => '0');
      end if;
    end if;
  end process;
  led_o <= led;

end architecture;