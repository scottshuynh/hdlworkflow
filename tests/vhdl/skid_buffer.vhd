library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.standard_pkg.all;
use work.array_pkg.all;

entity skid_buffer is
  generic (
    DATA_W : positive;
    DEPTH  : positive
  );
  port (
    clk_i      : in    std_logic;
    rst_i      : in    std_logic := '0';
    ce_i       : in    std_logic := '1';
    src_data_i : in    std_logic_vector(DATA_W - 1 downto 0);
    src_vld_i  : in    std_logic;
    src_rdy_o  : out   std_logic;
    dst_data_o : out   std_logic_vector(DATA_W - 1 downto 0);
    dst_vld_o  : out   std_logic;
    dst_rdy_i  : in    std_logic
  );
end entity skid_buffer;

architecture rtl of skid_buffer is
  constant ZEROS_DATA          : std_logic_vector                                 := zeros(DATA_W);
  signal   z_src_data          : array_slv_t(0 to DEPTH - 1)(DATA_W - 1 downto 0) := zeros(DEPTH, DATA_W);
  signal   z_src_vld           : std_logic_vector(DEPTH - 1 downto 0)             := zeros(DEPTH);
  signal   src_rdy             : std_logic;

  constant IDX_W               : natural                      := ceil_log2(DEPTH) + 1;
  signal   z_src_data_idx      : unsigned(IDX_W - 1 downto 0) := (others => '0');
  signal   prev_z_src_data_idx : unsigned(IDX_W - 1 downto 0);

  signal buff                  : std_logic;
  signal drain                 : std_logic;

begin

  assert DEPTH >= 2
    report "DEPTH must be greater than or equal to 2"
    severity FAILURE;

  src_rdy             <= not (and z_src_vld) and not rst_i;
  buff                <= src_rdy and src_vld_i;
  drain               <= dst_rdy_i and or z_src_vld;
  prev_z_src_data_idx <= z_src_data_idx - 1;
  src_rdy_o           <= src_rdy;

  process (clk_i) is
  begin
    if rising_edge(clk_i) then
      if (ce_i = '1') then
        if (drain = '1') then
          z_src_data(DEPTH - 1)         <= ZEROS_DATA;
          z_src_vld(DEPTH - 1)          <= '0';
          z_src_data(0 to DEPTH - 2)    <= z_src_data(1 to DEPTH - 1);
          z_src_vld(DEPTH - 2 downto 0) <= z_src_vld(DEPTH - 1 downto 1);
          z_src_data_idx                <= z_src_data_idx - 1;
        end if;

        if (buff = '1') then
          if (drain = '1') then
            z_src_data(to_integer(prev_z_src_data_idx)) <= src_data_i;
            z_src_vld(to_integer(prev_z_src_data_idx))  <= src_vld_i;
          else
            z_src_data(to_integer(z_src_data_idx)) <= src_data_i;
            z_src_vld(to_integer(z_src_data_idx))  <= src_vld_i;
          end if;

          z_src_data_idx <= z_src_data_idx + 1;
        end if;

        if (buff and drain) then
          z_src_data_idx <= z_src_data_idx;
        end if;

        if (rst_i = '1') then
          z_src_data     <= zeros(DEPTH, DATA_W);
          z_src_vld      <= zeros(DEPTH);
          z_src_data_idx <= zeros(IDX_W);
        end if;
      end if;
    end if;
  end process;

  dst_data_o <= z_src_data(0);
  dst_vld_o  <= z_src_vld(0);

end architecture rtl;
